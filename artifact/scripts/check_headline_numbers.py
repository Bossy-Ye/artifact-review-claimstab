#!/usr/bin/env python3
"""Verify CLAIMSTAB-QC headline numbers from locked artifact data.

The checks here are deliberately read-only. They do not rerun quantum
experiments, regenerate locked CSVs, or edit paper files.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import math
import subprocess
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROOT = REPO_ROOT / "artifact"
REPORT_DIR = ARTIFACT_ROOT / "outputs" / "reports"
HEADLINE_REPORT = REPORT_DIR / "headline_number_check.md"


@dataclass
class Check:
    name: str
    expected: str
    actual: str
    status: str
    source: str
    critical: bool = True
    note: str = ""


def _resolve(path: str):
    """Prefer the repo-root source; fall back to the vendored copy under
    artifact/results/ so the checks run when only artifact/ is shipped."""
    full = REPO_ROOT / path
    if full.exists():
        return full
    vendored = REPO_ROOT / "artifact" / "results" / path
    return vendored if vendored.exists() else full


def read_csv(path: str) -> pd.DataFrame | None:
    full = _resolve(path)
    if not full.exists():
        return None
    return pd.read_csv(full)


def add_exact(checks: list[Check], name: str, expected, actual, source: str, critical: bool = True, note: str = "") -> None:
    status = "PASS" if str(actual) == str(expected) else "FAIL"
    checks.append(Check(name, str(expected), str(actual), status, source, critical, note))


def add_bool(checks: list[Check], name: str, expected: str, ok: bool, actual: str, source: str, critical: bool = True, note: str = "") -> None:
    checks.append(Check(name, expected, actual, "PASS" if ok else "FAIL", source, critical, note))


def add_missing(checks: list[Check], name: str, expected: str, source: str, critical: bool = True, note: str = "") -> None:
    checks.append(Check(name, expected, "MISSING", "MISSING", source, critical, note))


def add_warning(checks: list[Check], name: str, expected: str, actual: str, source: str, note: str) -> None:
    checks.append(Check(name, expected, actual, "WARNING", source, False, note))


def value_counts(df: pd.DataFrame, column: str) -> dict[str, int]:
    return {str(k): int(v) for k, v in df[column].value_counts(dropna=False).items()}


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unavailable"


def collect_checks() -> list[Check]:
    checks: list[Check] = []

    papers = read_csv("artifact/field_study/corpus/paper_list_250_screened.csv")
    if papers is None:
        add_missing(checks, "papers_processed", "119", "artifact/field_study/corpus/paper_list_250_screened.csv")
    else:
        included = int((papers["screening_decision"].astype(str).str.lower() == "include").sum())
        add_exact(checks, "papers_processed", 119, included, "artifact/field_study/corpus/paper_list_250_screened.csv")

    field = read_csv("paper/output/figures/section5/field_protocol_summary.csv")
    if field is None:
        for name, expected in [
            ("stage1_candidates", 630),
            ("stage2_verified", 628),
            ("accepted_claims", 455),
            ("confidence_distribution", "HIGH=343, MEDIUM=112, LOW=0"),
            ("quality_interventions", "7 cleanup papers; 6 centrality corrections (+5 net)"),
            ("paradigm_breakdown", "compilation=142, variational=313"),
        ]:
            add_missing(checks, name, str(expected), "paper/output/figures/section5/field_protocol_summary.csv")
    else:
        joined = "\n".join(field.astype(str).agg(" ".join, axis=1).tolist())
        add_bool(checks, "stage1_candidates", "630", "630" in joined, "found 630" if "630" in joined else "not found", "paper/output/figures/section5/field_protocol_summary.csv")
        add_bool(checks, "stage2_verified", "628", "628" in joined and "99.7" in joined, "found 628 / 99.7%" if "628" in joined else "not found", "paper/output/figures/section5/field_protocol_summary.csv")
        add_bool(checks, "accepted_claims", "455", "455" in joined and "72.5" in joined, "found 455 / 72.5%" if "455" in joined else "not found", "paper/output/figures/section5/field_protocol_summary.csv")
        add_bool(checks, "confidence_distribution", "HIGH=343, MEDIUM=112, LOW=0", all(x in joined for x in ["343", "112", "0 LOW"]), "present" if all(x in joined for x in ["343", "112", "0 LOW"]) else "not found", "paper/output/figures/section5/field_protocol_summary.csv")
        add_bool(checks, "quality_interventions", "7 cleanup papers; 6 centrality corrections (+5 net)", all(x in joined for x in ["7 cleanup", "6 centrality", "+5"]), "present" if all(x in joined for x in ["7 cleanup", "6 centrality", "+5"]) else "not found", "paper/output/figures/section5/field_protocol_summary.csv")
        add_bool(checks, "paradigm_breakdown", "compilation=142, variational=313", all(x in joined for x in ["142 compilation", "313 variational"]), "present" if all(x in joined for x in ["142 compilation", "313 variational"]) else "not found", "paper/output/figures/section5/field_protocol_summary.csv")

    # Raw pre-adjudication extraction file (457 rows). These check the raw input,
    # which is unchanged; the corrected source-grounded counts are checked below
    # against artifact/corrected_headline_counts.csv.
    claims = read_csv("artifact/field_study/claims/extracted_claims_457.csv")
    raw_note = "Raw pre-adjudication extraction; corrected counts in artifact/corrected_headline_counts.csv."
    if claims is None:
        add_missing(checks, "raw_extracted_rows", "457 rows", "artifact/field_study/claims/extracted_claims_457.csv")
    else:
        add_exact(checks, "raw_extracted_rows", 457, len(claims), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        op_counts = value_counts(claims, "operationalizability_category")
        add_exact(checks, "raw_audit_eligible", 76, op_counts.get("audit_eligible_operationalizable", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        add_exact(checks, "raw_verification_only", 2, op_counts.get("verification_eligible_operationalizable", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        add_exact(checks, "raw_not_yet_operationalizable", 379, op_counts.get("not_operationalizable_or_borderline", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        conf = value_counts(claims, "confidence")
        add_exact(checks, "raw_claim_confidence_HIGH", 345, conf.get("HIGH", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        add_exact(checks, "raw_claim_confidence_MEDIUM", 112, conf.get("MEDIUM", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        add_exact(checks, "raw_claim_confidence_LOW", 0, conf.get("LOW", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        paradigms = value_counts(claims, "paradigm")
        add_exact(checks, "raw_field_paradigm_compilation", 143, paradigms.get("compilation", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)
        add_exact(checks, "raw_field_paradigm_variational", 314, paradigms.get("variational", 0), "artifact/field_study/claims/extracted_claims_457.csv", note=raw_note)

    # Derived source-grounded RQ1 decision crosscheck. Unlike the raw flags above,
    # this file applies the documented 16-row crosscheck to every candidate row.
    # The paper-facing count is carried by corrected_headline_counts.csv and its
    # source-grounded adjudication support.
    decision_registry = read_csv("artifact/field_study/claims/rq1_claim_decisions_457.csv")
    derived_targets: dict[str, int] = {}
    if decision_registry is None:
        for name, expected in [
            ("accepted_comparative_claims", 455),
            ("claim_card_specifiable", 175),
            ("scalar_directional", 145),
            ("planning_feasible", 93),
            ("scalar_oriented_planning", 79),
            ("materialized_rq2", 8),
        ]:
            add_missing(
                checks,
                f"derived_{name}",
                str(expected),
                "artifact/field_study/claims/rq1_claim_decisions_457.csv",
            )
    else:
        add_exact(
            checks,
            "rq1_decision_crosscheck_rows",
            457,
            len(decision_registry),
            "artifact/field_study/claims/rq1_claim_decisions_457.csv",
        )

        def final_true(column: str) -> int:
            return int(decision_registry[column].astype(str).str.lower().eq("true").sum())

        derived_targets = {
            "accepted_comparative_claims": final_true("final_accepted_comparative_claim"),
            "claim_card_specifiable": final_true("final_claim_card_specifiable"),
            "scalar_directional": final_true("final_scalar_directional"),
            "planning_feasible": final_true("final_planning_feasible"),
            "scalar_oriented_planning": final_true("final_scalar_oriented_planning"),
            "materialized_rq2": final_true("final_materialized_rq2"),
        }
        accepted_final = decision_registry.loc[
            decision_registry["final_accepted_comparative_claim"].astype(str).str.lower() == "true"
        ]
        final_confidence = value_counts(accepted_final, "confidence")
        final_paradigms = value_counts(accepted_final, "paradigm")
        add_exact(checks, "final_claim_confidence_HIGH", 343, final_confidence.get("HIGH", 0), "artifact/field_study/claims/rq1_claim_decisions_457.csv")
        add_exact(checks, "final_claim_confidence_MEDIUM", 112, final_confidence.get("MEDIUM", 0), "artifact/field_study/claims/rq1_claim_decisions_457.csv")
        add_exact(checks, "final_claim_confidence_LOW", 0, final_confidence.get("LOW", 0), "artifact/field_study/claims/rq1_claim_decisions_457.csv")
        add_exact(checks, "final_field_paradigm_compilation", 142, final_paradigms.get("compilation", 0), "artifact/field_study/claims/rq1_claim_decisions_457.csv")
        add_exact(checks, "final_field_paradigm_variational", 313, final_paradigms.get("variational", 0), "artifact/field_study/claims/rq1_claim_decisions_457.csv")
        relation_counts = value_counts(
            decision_registry.loc[
                decision_registry["final_claim_card_specifiable"].astype(str).str.lower() == "true"
            ],
            "final_relation_family",
        )
        derived_targets.update(
            {
                "non_scalar_in_175": derived_targets["claim_card_specifiable"] - derived_targets["scalar_directional"],
                "multi_objective_in_175": relation_counts.get("multi_objective", 0),
                "categorical_equality_in_175": relation_counts.get("categorical_or_equality", 0),
                "crossover_regional_in_175": relation_counts.get("crossover_or_regional", 0),
            }
        )
        expected_derived = {
            "accepted_comparative_claims": 455,
            "claim_card_specifiable": 175,
            "scalar_directional": 145,
            "planning_feasible": 93,
            "scalar_oriented_planning": 79,
            "materialized_rq2": 8,
            "non_scalar_in_175": 30,
            "multi_objective_in_175": 26,
            "categorical_equality_in_175": 2,
            "crossover_regional_in_175": 2,
        }
        for name, expected in expected_derived.items():
            add_exact(
                checks,
                f"derived_{name}",
                expected,
                derived_targets[name],
                "artifact/field_study/claims/rq1_claim_decisions_457.csv",
                note="Derived row-level crosscheck; paper-facing counts are in corrected_headline_counts.csv.",
            )

    paper_registry = read_csv("artifact/field_study/corpus/final_rq1_paper_registry_119.csv")
    if paper_registry is None:
        add_missing(
            checks,
            "final_rq1_paper_registry_rows",
            "119",
            "artifact/field_study/corpus/final_rq1_paper_registry_119.csv",
        )
    else:
        add_exact(
            checks,
            "final_rq1_paper_registry_rows",
            119,
            len(paper_registry),
            "artifact/field_study/corpus/final_rq1_paper_registry_119.csv",
        )
        contributes = int(
            paper_registry["contributes_accepted_claims"].astype(str).str.lower().eq("true").sum()
        )
        add_exact(
            checks,
            "papers_contributing_accepted_claims",
            118,
            contributes,
            "artifact/field_study/corpus/final_rq1_paper_registry_119.csv",
            note="The screened corpus has 119 included papers; 118 contribute one or more accepted claims.",
        )

    # The paper-facing corrected-count table must agree with the derived row-level
    # decision crosscheck.
    corrected = read_csv("artifact/corrected_headline_counts.csv")
    corrected_targets = {
        "accepted_comparative_claims": 455,
        "claim_card_specifiable": 175,
        "scalar_directional": 145,
        "planning_feasible": 93,
        "scalar_oriented_planning": 79,
        "auditable_designs_from_79": 53,
        "materialized_rq2": 8,
        "non_scalar_in_175": 30,
        "multi_objective_in_175": 26,
        "categorical_equality_in_175": 2,
        "crossover_regional_in_175": 2,
    }
    if corrected is None:
        for name, expected in corrected_targets.items():
            add_missing(checks, f"corrected_{name}", str(expected), "artifact/corrected_headline_counts.csv")
    else:
        cmap = {str(r["count_name"]): str(r["corrected_value"]) for _, r in corrected.iterrows()}
        for name, expected in corrected_targets.items():
            row_level_value = derived_targets.get(name, expected)
            add_exact(
                checks,
                f"corrected_{name}",
                row_level_value,
                cmap.get(name, "MISSING"),
                "artifact/corrected_headline_counts.csv",
                note="Paper-facing corrected count crosschecked against the derived row-level decisions.",
            )

    tiers = read_csv("artifact/external_audit/materialization/materialization_tiers_76.csv")
    if tiers is None:
        for name, expected in [("T1", 8), ("T2", 0), ("T3", 58), ("T4", 10), ("completed_external_audits", 8)]:
            add_missing(checks, name, str(expected), "artifact/external_audit/materialization/materialization_tiers_76.csv")
    else:
        tier_counts = value_counts(tiers, "materialization_tier")
        add_exact(checks, "materialization_rows", 76, len(tiers), "artifact/external_audit/materialization/materialization_tiers_76.csv")
        add_exact(checks, "T1", 8, tier_counts.get("T1", 0), "artifact/external_audit/materialization/materialization_tiers_76.csv")
        add_exact(checks, "T2", 0, tier_counts.get("T2", 0), "artifact/external_audit/materialization/materialization_tiers_76.csv")
        add_exact(checks, "T3", 58, tier_counts.get("T3", 0), "artifact/external_audit/materialization/materialization_tiers_76.csv")
        add_exact(checks, "T4", 10, tier_counts.get("T4", 0), "artifact/external_audit/materialization/materialization_tiers_76.csv")
        completed = int((tiers["completed_external_audit"].astype(str).str.lower() == "yes").sum())
        add_exact(checks, "completed_external_audits_in_tiers", 8, completed, "artifact/external_audit/materialization/materialization_tiers_76.csv")

    missing = read_csv("artifact/external_audit/materialization/materialization_missing_elements.csv")
    if missing is None:
        for elem in ["artifact", "hyperparameters", "baseline", "resource_budget", "instance_generator", "optimizer"]:
            add_missing(checks, f"missing_{elem}", "expected multi-label count", "artifact/external_audit/materialization/materialization_missing_elements.csv", critical=False)
    else:
        got = dict(zip(missing["missing_element"].astype(str), missing["count"].astype(int)))
        expected_missing = {
            "artifact": 68,
            "hyperparameters": 56,
            "baseline": 43,
            "resource_budget": 30,
            "instance_generator": 27,
            "optimizer": 23,
        }
        for elem, exp in expected_missing.items():
            add_exact(checks, f"missing_{elem}", exp, got.get(elem, 0), "artifact/external_audit/materialization/materialization_missing_elements.csv", critical=False, note="Multi-label count; values need not sum to 68 or 76.")

    validation = read_csv("artifact/external_audit/materialization/materialization_tier_validation.csv")
    if validation is None:
        add_missing(checks, "T3_T4_validation_rows", "68 rows", "artifact/external_audit/materialization/materialization_tier_validation.csv")
    else:
        add_exact(checks, "T3_T4_validation_rows", 68, len(validation), "artifact/external_audit/materialization/materialization_tier_validation.csv")
        cur = value_counts(validation, "current_tier")
        add_exact(checks, "T3_validation_rows", 58, cur.get("T3", 0), "artifact/external_audit/materialization/materialization_tier_validation.csv")
        add_exact(checks, "T4_validation_rows", 10, cur.get("T4", 0), "artifact/external_audit/materialization/materialization_tier_validation.csv")
        actions = value_counts(validation, "recommended_action")
        add_exact(checks, "T3_T4_reconsider_rows", 0, sum(v for k, v in actions.items() if "reconsider" in k.lower()), "artifact/external_audit/materialization/materialization_tier_validation.csv")

    qvans = read_csv("artifact/external_audit/feasibility_notes/qvans_feasibility_table.csv")
    if qvans is None:
        add_missing(checks, "QVAns_final_decision", "keep_T3 for both high-risk rows", "artifact/external_audit/feasibility_notes/qvans_feasibility_table.csv")
    else:
        recommended_col = "recommended_tier"
        if recommended_col in qvans.columns:
            keep_t3 = int((qvans[recommended_col].astype(str) == "keep_T3").sum())
            add_exact(checks, "QVAns_keep_T3_rows", 2, keep_t3, "artifact/external_audit/feasibility_notes/qvans_feasibility_table.csv")
        else:
            add_warning(checks, "QVAns_keep_T3_rows", "2", "column missing", "artifact/external_audit/feasibility_notes/qvans_feasibility_table.csv", "Cannot mechanically verify recommended tier column.")

    external = read_csv("paper/output/figures/section5/external_forest_data.csv")
    if external is None:
        add_missing(checks, "external_audit_rows", "8 rows", "paper/output/figures/section5/external_forest_data.csv")
    else:
        add_exact(checks, "external_audit_rows", 8, len(external), "paper/output/figures/section5/external_forest_data.csv")
        cls = value_counts(external, "classification")
        add_exact(checks, "external_Sustained", 2, cls.get("Sustained", 0), "paper/output/figures/section5/external_forest_data.csv")
        add_exact(checks, "external_Unresolved", 4, cls.get("Unresolved", 0), "paper/output/figures/section5/external_forest_data.csv")
        add_exact(checks, "external_Reversed", 2, cls.get("Reversed", 0), "paper/output/figures/section5/external_forest_data.csv")
        dom = value_counts(external, "domain")
        add_exact(checks, "external_domain_compilation", 5, dom.get("compilation", 0), "paper/output/figures/section5/external_forest_data.csv")
        add_exact(checks, "external_domain_benchmark", 1, dom.get("benchmark", 0), "paper/output/figures/section5/external_forest_data.csv")
        add_exact(checks, "external_domain_optimization", 2, dom.get("optimization", 0), "paper/output/figures/section5/external_forest_data.csv")
        expected_rows = {
            "EX-C1": (1.000, 0.954, 1.000, "Sustained"),
            "EX-C2": (1.000, 0.954, 1.000, "Sustained"),
            "EX-C3": (0.775, 0.672, 0.853, "Unresolved"),
            "EX-C4": (0.562, 0.453, 0.666, "Unresolved"),
            "EX-C5": (0.550, 0.441, 0.654, "Unresolved"),
            "EX-C6": (0.425, 0.323, 0.534, "Unresolved"),
            "EX-C7": (0.000, 0.000, 0.046, "Reversed"),
            "EX-C8": (0.000, 0.000, 0.046, "Reversed"),
        }
        for label, (s_hat, low, high, klass) in expected_rows.items():
            row = external.loc[external["figure_label"] == label]
            if row.empty:
                add_bool(checks, f"{label}_external_values", f"{s_hat:.3f} [{low:.3f}, {high:.3f}], {klass}", False, "missing row", "paper/output/figures/section5/external_forest_data.csv")
            else:
                r = row.iloc[0]
                ok = (
                    math.isclose(float(r["s_hat"]), s_hat, abs_tol=0.0006)
                    and math.isclose(float(r["wilson_lower"]), low, abs_tol=0.001)
                    and math.isclose(float(r["wilson_upper"]), high, abs_tol=0.001)
                    and str(r["classification"]) == klass
                )
                actual = f"{float(r['s_hat']):.3f} [{float(r['wilson_lower']):.3f}, {float(r['wilson_upper']):.3f}], {r['classification']}"
                add_bool(checks, f"{label}_external_values", f"{s_hat:.3f} [{low:.3f}, {high:.3f}], {klass}", ok, actual, "paper/output/figures/section5/external_forest_data.csv")

    canonical = read_csv("paper/output/figures/section5/canonical24_forest_data.csv")
    if canonical is None:
        add_missing(checks, "canonical_24_rows", "24 rows", "paper/output/figures/section5/canonical24_forest_data.csv")
    else:
        add_exact(checks, "canonical_24_rows", 24, len(canonical), "paper/output/figures/section5/canonical24_forest_data.csv")
        ccls = value_counts(canonical, "classification")
        add_exact(checks, "canonical_Sustained", 10, ccls.get("Sustained", 0), "paper/output/figures/section5/canonical24_forest_data.csv")
        add_exact(checks, "canonical_Unresolved", 14, ccls.get("Unresolved", 0), "paper/output/figures/section5/canonical24_forest_data.csv")
        add_exact(checks, "canonical_Reversed", 0, ccls.get("Reversed", 0), "paper/output/figures/section5/canonical24_forest_data.csv")
        sw = canonical[canonical["paradigm"] == "software-stack"]
        opt = canonical[canonical["paradigm"] == "optimization"]
        add_exact(checks, "canonical_software_stack_Sustained", 9, int((sw["classification"] == "Sustained").sum()), "paper/output/figures/section5/canonical24_forest_data.csv")
        add_exact(checks, "canonical_optimization_Sustained", 1, int((opt["classification"] == "Sustained").sum()), "paper/output/figures/section5/canonical24_forest_data.csv")
        add_exact(checks, "canonical_optimization_Unresolved", 14, int((opt["classification"] == "Unresolved").sum()), "paper/output/figures/section5/canonical24_forest_data.csv")

    cal = read_csv("data/synthetic/calibration_results.csv")
    if cal is None:
        add_missing(checks, "wilson_coverage_percent", "94.97%", "data/synthetic/calibration_results.csv")
    else:
        actual = float(cal["ci_contains_s_true"].mean() * 100.0)
        add_bool(checks, "wilson_coverage_percent", "94.97%", math.isclose(actual, 94.97, abs_tol=0.01), f"{actual:.2f}%", "data/synthetic/calibration_results.csv")

    syn = read_csv("output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv")
    ctrl = read_csv("output/paper/icse_pack/derived/ANALYSIS/synthetic_control_sanity.csv")
    if syn is None or ctrl is None:
        add_missing(checks, "synthetic_reversed_corpus", "9/9 Reversed", "synthetic reversed files")
    else:
        expanded_rev = int((syn["actual_classification"] == "Reversed").sum())
        original_rev = int(((ctrl["control_id"] == "shuffled_reversed") & (ctrl["reporting_status"] == "Reversed")).sum())
        total = len(syn) + 1
        add_exact(checks, "synthetic_reversed_corpus", "9/9", f"{expanded_rev + original_rev}/{total}", "output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv + synthetic_control_sanity.csv")

    chem = read_csv("output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv")
    if chem is None:
        add_missing(checks, "chemistry_reversed_cases", "17/18 Reversed; 18/18 not Sustained", "output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv")
    else:
        refuted = int((chem["claim_validation_outcome"] == "refuted").sum())
        not_sustained = int((chem["baseline_claim_holds"] == False).sum())  # noqa: E712
        add_exact(checks, "chemistry_refuted_cases", "17/18", f"{refuted}/{len(chem)}", "output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv")
        add_exact(checks, "chemistry_not_sustained_cases", "18/18", f"{not_sustained}/{len(chem)}", "output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv")
        add_exact(checks, "combined_reversed_detection", "26/27", f"{8 + 1 + refuted}/{8 + 1 + len(chem)}", "synthetic reversed + chemistry supporting files")

    variance = read_csv("paper/output/figures/section5/variance_decomposition_values.csv")
    if variance is None:
        add_missing(checks, "variance_attribution_summary", "software L1 ~=78%; optimization stack ~=11%", "paper/output/figures/section5/variance_decomposition_values.csv", critical=False)
    else:
        sw_row = variance.loc[variance["paradigm"] == "Software-stack"].iloc[0]
        opt_row = variance.loc[variance["paradigm"] == "Optimization"].iloc[0]
        sw_l1 = float(sw_row["L1 compilation"]) * 100
        opt_stack = float(opt_row["L1 compilation"] + opt_row["L2 execution"] + opt_row["L3 backend"]) * 100
        add_bool(checks, "variance_software_L1_percent", "approximately 78%", 77.0 <= sw_l1 <= 79.0, f"{sw_l1:.1f}%", "paper/output/figures/section5/variance_decomposition_values.csv", critical=False)
        add_bool(checks, "variance_optimization_stack_percent", "approximately 11%", 10.0 <= opt_stack <= 12.0, f"{opt_stack:.1f}%", "paper/output/figures/section5/variance_decomposition_values.csv", critical=False)

    # Manuscript-facing 47-claim cluster-bootstrap aggregate
    # (24 canonical + 8 external + 15 RQ3 controlled-validation suite;
    # legacy four-regime L3 superseded and not double-counted).
    cluster47 = read_csv("paper/output/figures/section5/cluster_bootstrap_47.csv")
    if cluster47 is None:
        add_missing(checks, "cluster_bootstrap_agreement_47", "47/47", "paper/output/figures/section5/cluster_bootstrap_47.csv")
    else:
        same = cluster47["same_classification"].astype(str).str.lower().eq("true").sum()
        add_exact(checks, "cluster_bootstrap_agreement_47", "47/47", f"{int(same)}/{len(cluster47)}", "paper/output/figures/section5/cluster_bootstrap_47.csv")

    sens = read_csv("paper/output/figures/section5/sensitivity_summary.csv")
    if sens is None:
        add_missing(checks, "sensitivity_summary", "tau/N/toggle checks", "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
    else:
        def reclass(analysis: str, setting: str) -> int | None:
            row = sens[(sens["analysis"].astype(str) == analysis) & (sens["setting"].astype(str) == setting)]
            if row.empty:
                return None
            return int(row.iloc[0]["reclassifications_vs_locked"])

        add_exact(checks, "tau_0.90_reclassifications", 0, reclass("tau", "0.9"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "tau_0.95_reclassifications", 0, reclass("tau", "0.95"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "tau_0.99_reclassifications", 10, reclass("tau", "0.99"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "N_40_reclassifications", 10, reclass("N", "40"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "N_80_reclassifications", 1, reclass("N", "80"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "N_120_reclassifications", 1, reclass("N", "120"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "N_160_reclassifications", 0, reclass("N", "160"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)
        add_exact(checks, "algorithmic_stochasticity_toggle", 0, reclass("algorithmic_stochasticity_placement", "metadata_toggle"), "paper/output/figures/section5/sensitivity_summary.csv", critical=False)

    practical = read_csv("paper/output/figures/section5/practical_stability_results_table.csv")
    if practical is None:
        add_missing(checks, "practical_stability", "30 considered / 13 analyzed / 17 skipped / 0 changed", "paper/output/figures/section5/practical_stability_results_table.csv", critical=False)
    else:
        total = practical.loc[practical["corpus"] == "Total"].iloc[0]
        add_exact(checks, "practical_total_considered", 30, int(total["total_considered"]), "paper/output/figures/section5/practical_stability_results_table.csv", critical=False)
        add_exact(checks, "practical_analyzed", 13, int(total["analyzed"]), "paper/output/figures/section5/practical_stability_results_table.csv", critical=False)
        add_exact(checks, "practical_skipped", 17, int(total["skipped"]), "paper/output/figures/section5/practical_stability_results_table.csv", critical=False)
        add_exact(checks, "practical_classification_changes", 0, int(total["classification_changes"]), "paper/output/figures/section5/practical_stability_results_table.csv", critical=False)

    baseline = read_csv("paper/output/figures/section5/baseline_diagnostic_fallback.csv")
    if baseline is None:
        add_missing(checks, "baseline_diagnostic", "diagnostic fallback available", "paper/output/figures/section5/baseline_diagnostic_fallback.csv", critical=False)
    else:
        joined = "\n".join(baseline.astype(str).agg(" ".join, axis=1).tolist())
        add_bool(checks, "baseline_single_run", "19 match / 5 oppose", "19 match" in joined and "5 oppose" in joined, "present" if "19 match" in joined else "not found", "paper/output/figures/section5/baseline_diagnostic_fallback.csv", critical=False)
        add_bool(checks, "baseline_seed_only_fallback", "24 Unresolved; 14 agree, 10 disagree", all(x in joined for x in ["24 Unresolved", "14 agree", "10 disagree"]), "present" if "24 Unresolved" in joined else "not found", "paper/output/figures/section5/baseline_diagnostic_fallback.csv", critical=False)

    diagnostic = _resolve("paper/output/figures/section5/perturbation_diagnostic.md")
    if diagnostic.exists():
        text = diagnostic.read_text(errors="ignore")
        for name, expected, needles in [
            ("matched_block_L1_available", "15/24", ["| L1 | 15 | 10 |"]),
            ("matched_block_L1_differences", "10/15", ["| L1 | 15 | 10 |"]),
            ("matched_block_L2_available", "3", ["| L2 | 3 | 0 |"]),
            ("matched_block_scope_available", "9", ["| scope | 9 | 0 |"]),
            ("matched_block_L3_no_subsets", "no qualifying subsets", ["| L3 | 0 | 0 |"]),
        ]:
            add_bool(checks, name, expected, all(n in text for n in needles), "present" if all(n in text for n in needles) else "not found", "paper/output/figures/section5/perturbation_diagnostic.md", critical=False)
    else:
        add_missing(checks, "matched_block_diagnostic", "available", "paper/output/figures/section5/perturbation_diagnostic.md", critical=False)

    # The six-row summary supports manuscript Table III. A separate 79-row file
    # supports record-level inspection without changing the manuscript-facing table.
    rq1_summary_src = "artifact/field_study/rq1_materialization_barrier_taxonomy.csv"
    rq1_records_src = "artifact/field_study/rq1_materialization_barrier_records_79.csv"
    rq1_summary = read_csv(rq1_summary_src)
    if rq1_summary is None:
        for name, exp in [
            ("rq1_materialization_total", 79),
            ("rq1_materialization_lockable_side", 53),
            ("rq1_materialization_boundary_side", 26),
            ("rq1_materialization_proxy_free_scoped", 8),
        ]:
            add_missing(checks, name, str(exp), rq1_summary_src)
    else:
        category = rq1_summary["category"].fillna("").astype(str)
        records = rq1_summary["records"].astype(int)
        proxy_free = int(records[category.str.contains("Proxy-free", regex=False)].sum())
        lockable_non_proxy = int(records[category.str.contains("Lockable", regex=False)].sum())
        boundary = int(records[category.str.contains("Boundary", regex=False)].sum())
        add_exact(checks, "rq1_materialization_total", 79, int(records.sum()), rq1_summary_src)
        add_exact(checks, "rq1_materialization_lockable_side", 53, proxy_free + lockable_non_proxy, rq1_summary_src)
        add_exact(checks, "rq1_materialization_boundary_side", 26, boundary, rq1_summary_src)
        add_exact(checks, "rq1_materialization_proxy_free_scoped", 8, proxy_free, rq1_summary_src)

    rq1_records = read_csv(rq1_records_src)
    if rq1_records is None:
        for name, expected in [
            ("rq1_source_supported_extensions", 43),
            ("rq1_source_materialized", 2),
            ("rq1_relation_specific_boundary", 20),
            ("rq1_verification_only_boundary", 2),
            ("rq1_no_lockable_design", 4),
        ]:
            add_missing(checks, name, str(expected), rq1_records_src)
    else:
        statuses = value_counts(rq1_records, "auditable_design_status")
        for name, expected, status in [
            ("rq1_source_supported_extensions", 43, "source_supported_extension"),
            ("rq1_source_materialized", 2, "source_materialized"),
            ("rq1_relation_specific_boundary", 20, "relation_specific_not_in_53"),
            ("rq1_verification_only_boundary", 2, "verification_only"),
            ("rq1_no_lockable_design", 4, "no_lockable_design"),
        ]:
            add_exact(checks, name, expected, statuses.get(status, 0), rq1_records_src)

    # RQ3 controlled diagnostic grids. These checks derive each summary's N and
    # preserved count directly from the shipped row-level grid, then verify the
    # paper-facing 0 S / 13 U / 2 R aggregate.
    diagnostics = {
        "l1_within_qiskit": {
            "L1Q-C1": (1200, 0, "Reversed"),
            "L1Q-C2": (1200, 400, "Unresolved"),
            "L1Q-C3": (1200, 0, "Reversed"),
        },
        "l2_sampling": {
            "L2-C1": (1800, 1074, "Unresolved"),
            "L2-C2": (1800, 1057, "Unresolved"),
            "L2-C3": (1800, 941, "Unresolved"),
        },
        "l3_noise": {
            "L3-C1": (270, 178, "Unresolved"),
            "L3-C2": (270, 174, "Unresolved"),
            "L3-C3": (270, 147, "Unresolved"),
        },
        "algo": {
            "ALGO-C1": (900, 726, "Unresolved"),
            "ALGO-C2": (900, 665, "Unresolved"),
            "ALGO-C3": (900, 592, "Unresolved"),
        },
        "combined_layer": {
            "COMB-C1": (1440, 866, "Unresolved"),
            "COMB-C2": (1440, 850, "Unresolved"),
            "COMB-C3": (1440, 723, "Unresolved"),
        },
    }
    rq3_verdicts: list[str] = []
    for stem, expected_claims in diagnostics.items():
        data_src = f"paper/output/figures/section5/{stem}_diagnostic_data.csv"
        summary_src = f"paper/output/figures/section5/{stem}_diagnostic_summary.csv"
        data = read_csv(data_src)
        summary = read_csv(summary_src)
        if data is None:
            add_missing(checks, f"rq3_{stem}_grid", str(sum(v[0] for v in expected_claims.values())), data_src)
            continue
        if summary is None:
            add_missing(checks, f"rq3_{stem}_summary", "3 rows", summary_src)
            continue
        add_exact(checks, f"rq3_{stem}_grid_rows", sum(v[0] for v in expected_claims.values()), len(data), data_src)
        add_exact(checks, f"rq3_{stem}_summary_rows", 3, len(summary), summary_src)
        for claim_id, (expected_n, expected_k, expected_verdict) in expected_claims.items():
            raw_claim = data.loc[data["claim_id"].astype(str) == claim_id]
            summary_claim = summary.loc[summary["claim_id"].astype(str) == claim_id]
            add_exact(checks, f"{claim_id}_raw_N", expected_n, len(raw_claim), data_src)
            raw_k = int(pd.to_numeric(raw_claim["preserves_direction"], errors="raise").sum())
            add_exact(checks, f"{claim_id}_raw_k", expected_k, raw_k, data_src)
            if summary_claim.empty:
                add_missing(checks, f"{claim_id}_summary", expected_verdict, summary_src)
                continue
            row = summary_claim.iloc[0]
            add_exact(checks, f"{claim_id}_summary_N", expected_n, int(row["n_cells"]), summary_src)
            add_exact(checks, f"{claim_id}_summary_k", raw_k, int(row["k_preserving"]), summary_src)
            add_exact(checks, f"{claim_id}_summary_verdict", expected_verdict, row["classification"], summary_src)
            add_exact(checks, f"{claim_id}_cluster_bootstrap", "1000/1000", f"{int(row['bootstrap_agreement'])}/{int(row['bootstrap_iterations'])}", summary_src)
            rq3_verdicts.append(str(row["classification"]))

    rq3_summary_src = "paper/output/figures/section5/rq3_controlled_validation_summary.csv"
    rq3_summary = read_csv(rq3_summary_src)
    if rq3_summary is None:
        add_missing(checks, "rq3_controlled_validation_summary", "5 diagnostics", rq3_summary_src)
    else:
        add_exact(checks, "rq3_controlled_validation_diagnostics", 5, len(rq3_summary), rq3_summary_src)
    add_exact(checks, "rq3_controlled_Sustained", 0, rq3_verdicts.count("Sustained"), "five RQ3 diagnostic summaries")
    add_exact(checks, "rq3_controlled_Unresolved", 13, rq3_verdicts.count("Unresolved"), "five RQ3 diagnostic summaries")
    add_exact(checks, "rq3_controlled_Reversed", 2, rq3_verdicts.count("Reversed"), "five RQ3 diagnostic summaries")

    gate_src = "artifact/external_audit/budget_sensitivity/reconstruction_gate_report.csv"
    gate = read_csv(gate_src)
    if gate is None:
        add_missing(checks, "tier1_reconstruction_gate", "4/4 PASS", gate_src)
    else:
        gate_pass = int(gate["gate_status"].astype(str).eq("PASS").sum())
        add_exact(checks, "tier1_reconstruction_gate", "4/4", f"{gate_pass}/{len(gate)}", gate_src)
        add_bool(
            checks,
            "tier1_reconstruction_cell_matches",
            "80/80 metric and label for all four records",
            bool((gate["metric_match"].astype(str).eq("80/80") & gate["label_match"].astype(str).eq("80/80")).all()),
            "all match" if len(gate) == 4 else f"{len(gate)} rows",
            gate_src,
        )
    diff_src = "artifact/external_audit/budget_sensitivity/reconstructed_vs_locked_diff.csv"
    reconstruction_diff = read_csv(diff_src)
    if reconstruction_diff is None:
        add_missing(checks, "tier1_reconstruction_diff_rows", "0", diff_src)
    else:
        add_exact(checks, "tier1_reconstruction_diff_rows", 0, len(reconstruction_diff), diff_src)

    return checks


def write_reports(checks: list[Check]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(checks)
    counts = {status: sum(1 for c in checks if c.status == status) for status in ["PASS", "FAIL", "MISSING", "WARNING"]}
    critical_failures = [c for c in checks if c.critical and c.status in {"FAIL", "MISSING"}]
    warning_rows = [c for c in checks if c.status == "WARNING"]
    lines = [
        "# Headline Number Check",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Repository commit: `{git_commit()}`",
        "",
        f"Summary: {counts['PASS']} passed, {counts['FAIL']} failed, {counts['MISSING']} missing, {counts['WARNING']} warnings out of {total} checks.",
        "",
        "| Status | Check | Expected | Actual | Source | Note |",
        "|---|---|---|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.status} | {c.name} | {c.expected} | {c.actual} | `{c.source}` | {c.note} |")
    lines.append("")
    if critical_failures:
        lines.append("Critical headline checks failed or are missing:")
        for c in critical_failures:
            lines.append(f"- `{c.name}`: expected {c.expected}, got {c.actual} from `{c.source}`.")
    else:
        lines.append("All required headline numerical claims checked by this script match the locked artifact data.")
    if warning_rows:
        lines.append("")
        lines.append("Warnings requiring wording or author review:")
        for c in warning_rows:
            lines.append(f"- `{c.name}`: {c.note} Actual: {c.actual}.")
    HEADLINE_REPORT.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Opt in to writing artifact/outputs/reports/headline_number_check.md. "
        "The default verification mode is read-only.",
    )
    args = parser.parse_args(argv)

    checks = collect_checks()
    counts = {status: sum(1 for c in checks if c.status == status) for status in ["PASS", "FAIL", "MISSING", "WARNING"]}
    critical_failures = [c for c in checks if c.critical and c.status in {"FAIL", "MISSING"}]

    if not args.write_report:
        # Concise default: write no report files.
        print(
            f"[headline-check] {counts['PASS']} pass / {counts['FAIL']} fail / "
            f"{counts['MISSING']} missing / {counts['WARNING']} warn out of {len(checks)} checks; "
            f"critical_failures={len(critical_failures)}"
        )
        for c in critical_failures:
            print(f"  CRITICAL {c.name}: expected {c.expected}, got {c.actual} (source {c.source})")
    else:
        write_reports(checks)
        for c in checks:
            print(f"[{c.status}] {c.name} = {c.actual} (expected {c.expected})")
        print(f"Report: {HEADLINE_REPORT.relative_to(REPO_ROOT)}")
    return 1 if critical_failures else 0


if __name__ == "__main__":
    sys.exit(main())
