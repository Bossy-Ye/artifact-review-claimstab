#!/usr/bin/env python3
"""EX-C7, the paper's worked example (Section V-B, Figs. 4-5).

Claim card artifact/claim_cards/EX-C7.yaml: Qiskit < Tket on two-qubit gate count.
Recomputes the 80 matched cells, the Wilson interval and the label from the
per-cell trace. Read-only.

Run from the repo root: python3 artifact/scripts/worked_example_exc7.py
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART / "src"))
from claimstab.audit import classify_direction_preservation  # noqa: E402
from claimstab.statistics import wilson_ci  # noqa: E402

CELLS = ART / "external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim3_measurements.csv"


def main() -> int:
    rows = list(csv.DictReader(open(CELLS, newline="")))
    total, by_level = Counter(), {}
    for r in rows:
        a, b = int(r["qiskit_cx_count"]), int(r["tket_cx_count"])
        cell = "preserved" if a < b else "tied" if a == b else "contradicted"
        total[cell] += 1
        by_level.setdefault(r["qiskit_optimization_level"], Counter())[cell] += 1
    for lvl in sorted(by_level):
        c = by_level[lvl]
        print(f"opt level {lvl}: {c['preserved']} preserved, {c['contradicted']} contradicted, {c['tied']} tied")
    k, n = total["preserved"], len(rows)
    ci = wilson_ci(k, n)
    label = classify_direction_preservation(ci.lower, ci.upper).value
    print(f"all: {k}/{n} preserved, {total['contradicted']} contradicted, {total['tied']} tied; "
          f"Wilson [{ci.lower:.3f}, {ci.upper:.3f}] -> {label}")
    ok = (k, total["contradicted"], total["tied"], n) == (0, 62, 18, 80) and label.startswith("Not preserved")
    print("[worked-example] matches the paper" if ok else "[worked-example] MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
