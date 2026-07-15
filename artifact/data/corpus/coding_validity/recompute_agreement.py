#!/usr/bin/env python3
"""Recompute the 120-item coding-validity agreement, Cohen's kappa, and confusion
matrices from source, with no external dependencies.

Source of truth (both label states live in one file, traced per claim):
  artifact/source_grounded_claim_adjudication.csv
    first  (initial worksheet annotation) <- previous_*    columns
    recode (independent re-coding)         <- adjudicated_* columns
The 120 sampled claims are the claim_id set in recode_labels_120.csv (this folder).

Committed outputs (next to this script):
  agreement_tables.csv      one row per coded field: n, distributions, % agreement, Cohen's kappa
  confusion_matrices.csv    first x recode cell counts per field

By default the script compares an in-memory recomputation with both committed
CSVs and writes nothing. Pass ``--write`` to replace the committed CSVs.

Run:  python3 recompute_agreement.py
"""
import argparse
import csv
import io
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ADJ = os.path.join(REPO, "artifact", "source_grounded_claim_adjudication.csv")
SAMPLE = os.path.join(HERE, "recode_labels_120.csv")

# field -> (first_column, recode_column); applicability = both labels present
FIELDS = [
    ("claim_card_specifiable", "previous_claim_card_specifiable", "adjudicated_claim_card_specifiable"),
    ("scalar_directional",     "previous_scalar_directional",     "adjudicated_scalar_directional"),
    ("planning_feasible",      "previous_planning_feasible",      "adjudicated_planning_feasible"),
    ("auditable_design",       "previous_broader_auditable_design", "adjudicated_broader_auditable_design"),
    ("proxy_free_exact_vs_non","previous_exact_proxy_free_materialized","adjudicated_exact_proxy_free_materialized"),
]
SKEWED_NOTE = "high-prevalence: kappa deflated by skewed marginals; read percent agreement + confusion matrix as primary"

def norm(v): return (v or "").strip().lower()

def cohen_kappa(pairs):
    n = len(pairs)
    if not n: return 0, 0.0, 0.0
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum((ca[c]/n) * (cb[c]/n) for c in set(ca) | set(cb))
    k = (po - pe) / (1 - pe) if (1 - pe) > 1e-12 else 1.0
    return n, round(po * 100, 2), round(k, 4)

AGREEMENT_FIELDS = ["field", "n_applicable", "first_label_dist",
                    "recode_label_dist", "percent_agreement", "cohen_kappa",
                    "kappa_status", "n_disagreements"]
CONFUSION_FIELDS = ["field", "first_label", "recode_label", "count"]


def compute_rows():
    with open(ADJ, newline="") as fh:
        adj = {r["claim_id"]: r for r in csv.DictReader(fh)}
    with open(SAMPLE, newline="") as fh:
        sample = [r["claim_id"] for r in csv.DictReader(fh)]
    agg_rows, conf_rows = [], []
    for name, pc, ac in FIELDS:
        pairs = []
        for cid in sample:
            r = adj.get(cid, {})
            a, b = norm(r.get(pc, "")), norm(r.get(ac, ""))
            if a in ("", "na", "n/a", "none") or b in ("", "na", "n/a", "none"):
                continue
            # proxy_free view: collapse to yes/no on exact-proxy-free
            pairs.append((a, b))
        n, pa, k = cohen_kappa(pairs)
        fd, rd = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
        # Flag only severe one-class dominance (>0.95 in either pass), where Cohen's
        # kappa is deflated despite high agreement (matches the paper's specifiability note).
        peak = max(list(fd.values()) + list(rd.values()), default=0)
        skewed = (peak / n > 0.95) if n else False
        agg_rows.append({"field": name, "n_applicable": n,
                         "first_label_dist": dict(fd), "recode_label_dist": dict(rd),
                         "percent_agreement": pa, "cohen_kappa": k,
                         "kappa_status": SKEWED_NOTE if skewed else "interpretable",
                         "n_disagreements": sum(a != b for a, b in pairs)})
        cells = Counter(pairs)
        for (a, b), c in sorted(cells.items()):
            conf_rows.append({"field": name, "first_label": a, "recode_label": b, "count": c})
    return agg_rows, conf_rows


def render_csv(fieldnames, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def read_exact(path):
    with open(path, newline="") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Replace the two committed derived CSVs. The default is read-only verification.",
    )
    args = parser.parse_args(argv)

    agg_rows, conf_rows = compute_rows()
    outputs = {
        os.path.join(HERE, "agreement_tables.csv"): render_csv(AGREEMENT_FIELDS, agg_rows),
        os.path.join(HERE, "confusion_matrices.csv"): render_csv(CONFUSION_FIELDS, conf_rows),
    }

    stale = []
    for path, content in outputs.items():
        if args.write:
            with open(path, "w", newline="") as fh:
                fh.write(content)
        elif not os.path.exists(path) or read_exact(path) != content:
            stale.append(path)

    for r in agg_rows:
        print(f"  {r['field']:26} n={r['n_applicable']:>3} agree={r['percent_agreement']:>6}% "
              f"kappa={r['cohen_kappa']:>7} ({r['kappa_status'].split(':')[0]})")
    if args.write:
        print("[agreement-check] wrote agreement_tables.csv and confusion_matrices.csv")
        return 0
    if stale:
        for path in stale:
            print(f"[agreement-check] STALE or missing: {os.path.relpath(path, REPO)}")
        print("[agreement-check] run with --write only if updating the locked derived tables")
        return 1
    print("[agreement-check] committed tables match the source recomputation (read-only)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
