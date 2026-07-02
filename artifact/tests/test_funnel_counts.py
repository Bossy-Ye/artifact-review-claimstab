"""Headline funnel + RQ2/RQ3/RQ4 distribution checks (reused from the repo's
tests/test_headline_numbers.py; data paths repointed to the self-contained artifact
tree). Reconciles the paper numbers from the shipped CSVs. Needs pandas."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

ART = Path(__file__).resolve().parents[1]  # artifact/
SEC5 = ART / "results/paper/output/figures/section5"


def test_corpus_funnel_counts() -> None:
    # 455 / 175 / 145 / 93 / 79 / 53 / 8 from the source-grounded authority.
    vals = {r["count_name"]: int(r["corrected_value"])
            for r in csv.DictReader(open(ART / "corrected_headline_counts.csv"))}
    assert vals["accepted_comparative_claims"] == 455
    assert vals["claim_card_specifiable"] == 175
    assert vals["scalar_directional"] == 145
    assert vals["planning_feasible"] == 93
    assert vals["scalar_oriented_planning"] == 79
    assert vals["auditable_designs_from_78"] == 53
    assert vals["materialized_rq2"] == 8


def test_external_audit_distribution() -> None:
    df = pd.read_csv(SEC5 / "external_forest_data.csv")
    counts = df["classification"].value_counts().to_dict()
    assert len(df) == 8
    assert counts.get("Sustained", 0) == 2
    assert counts.get("Unresolved", 0) == 4
    assert counts.get("Reversed", 0) == 2


def test_canonical_distribution() -> None:
    df = pd.read_csv(SEC5 / "canonical24_forest_data.csv")
    counts = df["classification"].value_counts().to_dict()
    assert len(df) == 24
    assert counts.get("Sustained", 0) == 10
    assert counts.get("Unresolved", 0) == 14
    assert counts.get("Reversed", 0) == 0


def test_cluster_bootstrap_47_agreement() -> None:
    df = pd.read_csv(SEC5 / "cluster_bootstrap_47.csv")
    assert len(df) == 47
    same = df["same_classification"].astype(str).str.lower().eq("true").sum()
    assert int(same) == 47


def test_sensitivity_exact_counts() -> None:
    df = pd.read_csv(SEC5 / "sensitivity_summary.csv")

    def value(analysis: str, setting: str) -> int:
        row = df[(df["analysis"].astype(str) == analysis) & (df["setting"].astype(str) == setting)]
        assert not row.empty
        return int(row.iloc[0]["reclassifications_vs_locked"])

    assert value("tau", "0.9") == 0
    assert value("tau", "0.95") == 0
    assert value("tau", "0.99") == 10
    assert value("N", "40") == 10
    assert value("N", "80") == 1
    assert value("N", "120") == 1
    assert value("N", "160") == 0
