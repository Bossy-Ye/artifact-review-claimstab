#!/usr/bin/env python3
"""RQ4 robustness alignment check.

Verifies that the artifact's recorded RQ4 evidence matches the paper's Table IV /
RQ4 finding: scalar-directional verdicts are *mostly stable under the tested checks,
but not uniformly*. Reads only locked artifact data (no recomputation of the audits)
and asserts the specific sensitivity / evidence-boundary facts the docs cite.

Self-contained and qiskit-free (csv only). Run from the repository root:

    python3 artifact/scripts/check_rq4_robustness.py

The default mode is read-only and exits 0 iff all checks pass. Pass
``--write-report`` to write artifact/outputs/reports/rq4_robustness_check.md.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T1 = ROOT / "artifact/external_audit/tier1_robustness"
SECTION5 = ROOT / "artifact/results/paper/output/figures/section5"
BUDGET = ROOT / "artifact/external_audit/budget_sensitivity"
REPORT = ROOT / "artifact/outputs/reports/rq4_robustness_check.md"

FORBIDDEN = [
    "all verdicts are stable", "stable under all", "robust under all",
    "fully robust", "no sensitivity", "unqualifiedly robust",
]


def rows(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Opt in to writing artifact/outputs/reports/rq4_robustness_check.md. "
        "The default verification mode is read-only.",
    )
    args = parser.parse_args(argv)

    results: list[tuple[bool, str]] = []

    def check(cond: bool, msg: str) -> None:
        results.append((bool(cond), msg))

    # ---- 1. EX-C7 primary 0/80 (per-cell + locked aggregate agree) ----
    prim = {r["record_id"]: r for r in rows(T1 / "tier1_primary_evidence.csv")}
    c7 = prim["EX-C7"]
    check(int(c7["preserved"]) == 0 and int(c7["N"]) == 80,
          f"EX-C7 primary preserved = {c7['preserved']}/{c7['N']} (expect 0/80)")
    fr = {r["claim_id"] if "claim_id" in r else r.get("figure_label"): r
          for r in rows(SECTION5 / "external_forest_data.csv")}
    c7f = next(r for r in rows(SECTION5 / "external_forest_data.csv") if r["figure_label"] == "EX-C7")
    check(int(c7f["k_preserved"]) == 0 and int(c7f["n_cells"]) == 80,
          f"EX-C7 locked aggregate = {c7f['k_preserved']}/{c7f['n_cells']} (expect 0/80)")

    # ---- 2. EX-C7 seed expansion 0/320 ----
    seed = rows(BUDGET / "expanded_seed_sensitivity.csv")
    c7_320 = [r for r in seed if r["record_id"] == "EX-C7" and int(r["N"]) == 320]
    check(len(c7_320) == 1 and int(c7_320[0]["k_preserved"]) == 0,
          f"EX-C7 seed expansion preserved = {c7_320[0]['k_preserved'] if c7_320 else '?'}/320 (expect 0/320)")
    # all replayable compiler records keep their primary label through N=320
    held = all(r["verdict"] == [s for s in seed if s["record_id"] == r["record_id"] and int(s["N"]) == 80][0]["verdict"]
               for r in seed if int(r["N"]) == 320)
    check(held, "all replayable compiler records keep their primary label through N=320")

    # ---- 3. EX-C3 cluster-bootstrap-sensitive; EX-C2/EX-C4 unavailable ----
    clu = {r["record_id"]: r for r in rows(T1 / "tier1_cluster_resampling.csv")}
    check("sensitive" in clu["EX-C3"]["cluster_status"].lower(),
          f"EX-C3 cluster status = '{clu['EX-C3']['cluster_status']}' (expect cluster-sensitive)")
    check("not-available" in clu["EX-C2"]["cluster_status"].lower(),
          "EX-C2 dependence check unavailable (per-cell trace not materialized)")
    check("not-available" in clu["EX-C4"]["cluster_status"].lower(),
          "EX-C4 dependence check unavailable (per-cell trace not materialized)")

    # ---- 4. Tie handling: EX-C7 0 preserved all policies; Reversed policy-bounded ----
    tie = [r for r in rows(T1 / "tier1_tie_policy_sensitivity.csv") if r["record_id"] == "EX-C7"]
    main = next(r for r in tie if r["tie_policy"] == "main_ties_nonpreserving")
    excl = next(r for r in tie if r["tie_policy"] == "ties_excluded")
    half = next(r for r in tie if r["tie_policy"] == "ties_half_preserving")
    check(main["verdict_projection"] == "Reversed" and float(main["preserved_effective"]) == 0.0,
          "EX-C7 main tie policy: Reversed, 0 preserved")
    check(float(main["preserved_effective"]) == 0.0 and float(excl["preserved_effective"]) == 0.0,
          "EX-C7 has 0 actual preserved cells under main and ties-excluded (contradicted-dominated)")
    check(float(half["preserved_effective"]) == 9.0,
          "EX-C7 ties-half-preserving is a projection (18 ties x 0.5 = 9 effective, not actual preserved)")
    check(excl["changed_from_primary"] == "True" and half["changed_from_primary"] == "True",
          "EX-C7 categorical Reversed label is policy-bounded (softens under alt. tie handling)")

    # ---- 5. Threshold tau: Tier-1 finite-N extreme labels soften at 0.99 only ----
    thr = rows(T1 / "tier1_threshold_sensitivity.csv")
    soft = {r["record_id"] for r in thr if r["tau"] == "0.99" and r["changed_from_primary"] == "True"}
    check(soft == {"EX-C1", "EX-C2", "EX-C7", "EX-C8"},
          f"tau=0.99 softens exactly the finite-N extreme labels {sorted(soft)} (expect EX-C1/C2/C7/C8)")
    nochange_lo = all(r["changed_from_primary"] == "False" for r in thr if r["tau"] in ("0.9", "0.95"))
    check(nochange_lo, "Tier-1 labels unchanged at tau in {0.90, 0.95}")

    # ---- 6. Canonical sensitivity_summary (tau shift-10, ALGO toggle 0) ----
    sens = rows(SECTION5 / "sensitivity_summary.csv")
    tau99 = next(r for r in sens if r["analysis"] == "tau" and r["setting"] == "0.99")
    check(int(tau99["reclassifications_vs_locked"]) == 10,
          f"canonical tau=0.99 shifts {tau99['reclassifications_vs_locked']} borderline cases (expect 10)")
    algo = next(r for r in sens if r["analysis"] == "algorithmic_stochasticity_placement")
    check(int(algo["reclassifications_vs_locked"]) == 0,
          "ALGO-axis bookkeeping changes 0 matched records / Wilson labels")

    # ---- 7. Practical-effect epsilon: no classification changes ----
    prac = rows(SECTION5 / "practical_stability_results_table.csv")
    total = next(r for r in prac if r["corpus"] == "Total")
    check(int(total["classification_changes"]) == 0,
          "practical-effect checks: 0 classification changes among analyzable records")

    # ---- 8. RQ4 finding wording present; forbidden over-claims absent ----
    summary = (T1 / "statistical_robustness_summary.md").read_text().lower()
    check("ex-c3" in summary and "ex-c7" in summary and "cluster" in summary,
          "summary records the EX-C3 cluster-sensitivity and EX-C7 boundary cases")
    blob = "\n".join(p.read_text().lower() for p in T1.glob("*.md"))
    bad = [f for f in FORBIDDEN if f in blob]
    check(not bad, f"no forbidden over-claim phrases in tier1_robustness docs (found: {bad})")

    # ---- optional report ----
    npass = sum(1 for ok, _ in results if ok)
    if args.write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# RQ4 Robustness Alignment Check", "",
                 f"{npass}/{len(results)} checks passed.", "",
                 "Verifies the artifact's recorded RQ4 evidence against the paper's Table IV /",
                 "RQ4 finding (verdicts mostly stable under tested checks, but not uniformly).", ""]
        for ok, msg in results:
            lines.append(f"- [{'PASS' if ok else 'FAIL'}] {msg}")
        REPORT.write_text("\n".join(lines) + "\n")

    for ok, msg in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {msg}")
    suffix = f" Report: {REPORT.relative_to(ROOT)}" if args.write_report else ""
    print(f"\n{npass}/{len(results)} checks passed.{suffix}")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
