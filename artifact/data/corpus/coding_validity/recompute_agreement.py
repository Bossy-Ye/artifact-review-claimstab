#!/usr/bin/env python3
"""Recompute the 120-item coding-validity agreement, Cohen's kappa, and confusion
matrices from source, with no external dependencies.

Source of truth (both label states live in one file, traced per claim):
  artifact/source_grounded_claim_adjudication.csv
    first  (initial worksheet annotation) <- previous_*    columns
    recode (independent re-coding)         <- adjudicated_* columns
The 120 sampled claims are the claim_id set in recode_labels_120.csv (this folder).

Outputs (written next to this script):
  agreement_tables.csv      one row per coded field: n, distributions, % agreement, Cohen's kappa
  confusion_matrices.csv    first x recode cell counts per field

Run:  python3 recompute_agreement.py
"""
import csv, os
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

def main():
    adj = {r["claim_id"]: r for r in csv.DictReader(open(ADJ, newline=""))}
    sample = [r["claim_id"] for r in csv.DictReader(open(SAMPLE, newline=""))]
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
    with open(os.path.join(HERE, "agreement_tables.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["field", "n_applicable", "first_label_dist",
            "recode_label_dist", "percent_agreement", "cohen_kappa", "kappa_status", "n_disagreements"])
        w.writeheader(); w.writerows(agg_rows)
    with open(os.path.join(HERE, "confusion_matrices.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["field", "first_label", "recode_label", "count"])
        w.writeheader(); w.writerows(conf_rows)
    for r in agg_rows:
        print(f"  {r['field']:26} n={r['n_applicable']:>3} agree={r['percent_agreement']:>6}% "
              f"kappa={r['cohen_kappa']:>7} ({r['kappa_status'].split(':')[0]})")

if __name__ == "__main__":
    main()
