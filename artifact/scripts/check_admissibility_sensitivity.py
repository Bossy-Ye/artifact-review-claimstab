#!/usr/bin/env python3
"""Admissibility sensitivity over the 79 scalar-directional planning records (RQ1).

Transpiler seed and optimization level are already admissible (Section III-C), so
treating them as admissible leaves the proxy-free count at 8. The other 71 records
are listed by recorded category from their per-record blocker codes.

Run from the repo root: python3 artifact/scripts/check_admissibility_sensitivity.py
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

RECORDS = Path(__file__).resolve().parents[1] / "field_study/rq1_materialization_barrier_records_79.csv"
SETTINGS = {"hyperparameters", "optimizer", "resource_budget"}
EXPECTED = {
    "source_supported_extension": 43,
    "source_materialized": 2,
    "relation_specific_not_in_53": 20,
    "verification_only": 2,
    "no_lockable_design": 4,
}


def main() -> int:
    rows = list(csv.DictReader(open(RECORDS, newline="")))
    tier1 = [r for r in rows if r["manuscript_group"] == "proxy_free_exact"]
    rest = [r for r in rows if r["manuscript_group"] != "proxy_free_exact"]
    by = Counter(r["auditable_design_status"] for r in rest)
    # A record is blocked by settings alone if every blocker code is a setting.
    settings_only = [
        r["record_id"] for r in rest
        if {r["primary_barrier"], *filter(None, r["secondary_barriers"].split(";"))} <= SETTINGS
    ]

    print(f"records: {len(rows)}")
    print(f"proxy-free (Tier 1): {len(tier1)}")
    print(f"seed and opt level admissible (Sec. III-C): {len(tier1)} (+0)")
    print(f"other {len(rest)} by recorded category:")
    for k, v in by.most_common():
        print(f"  {k:30} {v}")
    print(f"blocked by settings alone: {len(settings_only)}")
    print(f"counting source-materialized as proxy-free: {len(tier1) + by['source_materialized']}")

    ok = len(rows) == 79 and len(tier1) == 8 and dict(by) == EXPECTED and not settings_only
    print("[admissibility-check] " + ("matches Table III" if ok else "MISMATCH"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
