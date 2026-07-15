"""Headline funnel + RQ2/RQ3/RQ4 distribution checks (reused from the repo's
tests/test_headline_numbers.py; data paths repointed to the self-contained artifact
tree). Reconciles the paper numbers from the shipped CSVs. Needs pandas."""
from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import sys

import pandas as pd

ART = Path(__file__).resolve().parents[1]  # artifact/
SEC5 = ART / "results/paper/output/figures/section5"


def test_corpus_funnel_counts() -> None:
    rows = list(csv.DictReader(open(ART / "field_study/claims/rq1_claim_decisions_457.csv")))

    def count(column: str) -> int:
        return sum(row[column].lower() == "true" for row in rows)

    assert len(rows) == 457
    assert count("final_accepted_comparative_claim") == 455
    assert count("final_claim_card_specifiable") == 175
    assert count("final_scalar_directional") == 145
    assert count("final_planning_feasible") == 93
    assert count("final_scalar_oriented_planning") == 79
    assert count("final_materialized_rq2") == 8

    summary = list(csv.DictReader(open(ART / "field_study/rq1_materialization_barrier_taxonomy.csv")))
    assert len(summary) == 6
    assert sum(int(row["records"]) for row in summary) == 79
    assert sum(int(row["records"]) for row in summary if "Proxy-free" in row["category"]) == 8
    assert sum(int(row["records"]) for row in summary if "Lockable" in row["category"]) == 45
    assert sum(int(row["records"]) for row in summary if "Boundary" in row["category"]) == 26

    taxonomy = list(csv.DictReader(open(ART / "field_study/rq1_materialization_barrier_records_79.csv")))
    final_79 = {row["claim_id"] for row in rows if row["final_scalar_oriented_planning"] == "true"}
    taxonomy_ids = {row["claim_id"] for row in taxonomy}
    assert taxonomy_ids == final_79
    groups = {group: sum(row["manuscript_group"] == group for row in taxonomy)
              for group in {row["manuscript_group"] for row in taxonomy}}
    assert len(taxonomy) == 79
    assert groups == {
        "proxy_free_exact": 8,
        "auditable_non_exact": 45,
        "no_design_or_boundary": 26,
    }
    statuses = {status: sum(row["auditable_design_status"] == status for row in taxonomy)
                for status in {row["auditable_design_status"] for row in taxonomy}}
    assert statuses == {
        "exact": 8,
        "source_supported_extension": 43,
        "source_materialized": 2,
        "relation_specific_not_in_53": 20,
        "verification_only": 2,
        "no_lockable_design": 4,
    }
    final_exact = {row["claim_id"] for row in rows if row["final_materialized_rq2"] == "true"}
    taxonomy_exact = {row["claim_id"] for row in taxonomy if row["auditable_design_status"] == "exact"}
    assert taxonomy_exact == final_exact
    final_verification = {row["claim_id"] for row in rows if row["final_verification_only"] == "true"}
    taxonomy_verification = {
        row["claim_id"] for row in taxonomy if row["auditable_design_status"] == "verification_only"
    }
    assert taxonomy_verification == final_verification


def test_rq1_decision_crosscheck_and_paper_rollup_are_current() -> None:
    result = subprocess.run(
        [sys.executable, ART / "scripts/build_rq1_claim_decisions.py"],
        cwd=ART.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_screened_corpus_has_119_papers_and_118_contributors() -> None:
    rows = list(csv.DictReader(open(ART / "field_study/corpus/final_rq1_paper_registry_119.csv")))
    assert len(rows) == 119
    assert sum(row["contributes_accepted_claims"] == "true" for row in rows) == 118
    assert sum(int(row["final_accepted_claim_count"]) for row in rows) == 455


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
