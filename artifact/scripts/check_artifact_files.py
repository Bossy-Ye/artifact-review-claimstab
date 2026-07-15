#!/usr/bin/env python3
"""Check that the reviewer-facing CLAIMSTAB-QC artifact files exist.

This script is intentionally lightweight: it does not regenerate experiments
or mutate locked result files. By default it only verifies file availability;
report generation is an explicit opt-in.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "artifact" / "outputs" / "reports"
REPORT_PATH = REPORT_DIR / "artifact_file_check.md"


@dataclass(frozen=True)
class ExpectedFile:
    category: str
    path: str
    required: bool
    purpose: str


EXPECTED_FILES: list[ExpectedFile] = [
    ExpectedFile("root", "README.md", True, "anonymous artifact entry point"),
    ExpectedFile("root", "LICENSE", True, "artifact license"),
    ExpectedFile("environment", "requirements.txt", True, "compatible reviewer dependency ranges"),
    ExpectedFile("environment", "requirements-lock.txt", True, "tested Python 3.12 reviewer environment"),
    ExpectedFile("artifact docs", "artifact/ARTIFACT_MANIFEST.md", True, "top-level artifact map"),
    ExpectedFile("artifact docs", "artifact/PAPER_CLAIMS_TO_EVIDENCE.md", True, "paper claim to evidence mapping"),
    ExpectedFile("artifact docs", "artifact/README.md", True, "reviewer entry point + verification commands"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/paper_list_250_screened.csv", True, "119 included papers from screened corpus"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/inclusion_exclusion_criteria.md", True, "corpus selection protocol"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/search_protocol.md", True, "Google Scholar search-and-screen protocol bridge note; normalized provenance"),
    ExpectedFile("field corpus", "artifact/field_study/coding_protocol/coding_guide.md", True, "field-coding guide"),
    ExpectedFile("field corpus", "artifact/field_study/coding_protocol/claim_unitization_rules.md", True, "claim unitization rules"),
    ExpectedFile("field corpus", "artifact/field_study/claims/extraction_worksheet_template.csv", True, "worksheet template"),
    ExpectedFile("field corpus", "artifact/field_study/claims/extracted_claims_457.csv", True, "457 pre-adjudication claim candidates with evidence fields"),
    ExpectedFile("field corpus", "artifact/field_study/claims/rq1_claim_decisions_457.csv", True, "derived row-level RQ1 decision crosscheck; 455 accepted flags over all candidate rows"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/final_rq1_paper_registry_119.csv", True, "119-paper accepted-claim rollup (118 contributing)"),
    ExpectedFile("field corpus", "artifact/headline_count_final_crosscheck_decisions.csv", True, "16-row adjudication crosscheck overlay"),
    ExpectedFile("field corpus", "artifact/field_study/rq1_materialization_barrier_taxonomy.csv", True, "six-row RQ1 materialization summary supporting manuscript Table III"),
    ExpectedFile("field corpus", "artifact/field_study/rq1_materialization_barrier_records_79.csv", True, "79 record-level dispositions supporting inspection of the Table III summary"),
    ExpectedFile("field corpus", "artifact/field_study/claims/operationalizability_labels.csv", True, "O1-O7 labels"),
    ExpectedFile("field corpus", "artifact/field_study/claims/failed_criteria_by_claim.csv", True, "failed criteria labels"),
    ExpectedFile("field corpus", "artifact/field_study/coding_protocol/inter_rater_agreement.md", True, "IRR limitation / available notes"),
    ExpectedFile("field corpus", "artifact/field_study/coding_protocol/disagreement_resolution_notes.md", True, "resolution notes"),
    ExpectedFile("coding validity", "artifact/data/corpus/coding_validity/agreement_tables.csv", True, "120-item agreement + Cohen's kappa (92.11/0.835, 96.55/0.782, 100/1.000)"),
    ExpectedFile("coding validity", "artifact/data/corpus/coding_validity/confusion_matrices.csv", True, "120-item confusion matrices"),
    ExpectedFile("coding validity", "artifact/data/corpus/coding_validity/adjudication_records.csv", True, "120-item disagreement adjudication records"),
    ExpectedFile("coding validity", "artifact/data/corpus/coding_validity/recode_labels_120.csv", True, "120-item recode labels"),
    ExpectedFile("library bundle", "artifact/src/claimstab/inference/policies.py", True, "Wilson interval + S/U/R policy (verdict-core)"),
    ExpectedFile("library bundle", "artifact/src/claimstab/statistics/wilson.py", True, "wilson_ci (verdict-core)"),
    ExpectedFile("library bundle", "artifact/src/claimstab/audit/relation_checkers.py", True, "relation checkers (verdict-core)"),
    ExpectedFile("library bundle", "artifact/src/README.md", True, "verdict-core bundle guide"),
    ExpectedFile("corpus", "artifact/field_study/corpus/search_log.csv", True, "13-query retrieval log + per-query hit counts"),
    ExpectedFile("environment", "artifact/ENVIRONMENT.md", True, "reviewer deps + pinned full-framework toolchain"),
    ExpectedFile("library bundle", "artifact/tests/test_wilson_rule.py", True, "bundle smoke test: Wilson rule"),
    ExpectedFile("library bundle", "artifact/tests/test_manifest_loading.py", True, "bundle smoke test: RQ2 ledger/evidence manifests"),
    ExpectedFile("materialization", "artifact/external_audit/materialization/materialization_tiers_76.csv", True, "T1/T2/T3/T4 labels"),
    ExpectedFile("materialization", "artifact/external_audit/materialization/materialization_missing_elements.csv", True, "multi-label materialization barriers"),
    ExpectedFile("materialization", "artifact/external_audit/materialization/materialization_tier_validation.csv", True, "T3/T4 validation labels"),
    ExpectedFile("materialization", "artifact/external_audit/feasibility_notes/qvans_feasibility_review.md", True, "QVAns materialization-feasibility review"),
    ExpectedFile("materialization", "artifact/external_audit/feasibility_notes/qvans_feasibility_table.csv", True, "QVAns feasibility table"),
    ExpectedFile("external audit", "artifact/external_audit/mapping/source_mapping_anonymized.csv", True, "EX-C1..EX-C8 source mapping"),
    ExpectedFile("external audit", "artifact/external_audit/feasibility_notes/materialization_boundary_records.md", True, "external-claim materialization boundary records"),
    ExpectedFile("external audit", "paper/output/figures/section5/external_forest_data.csv", True, "8 external audit Wilson results"),
    ExpectedFile("external audit", "paper/output/figures/section5/per_claim_perturbations.csv", True, "external perturbation specification"),
    ExpectedFile("external audit", "artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2202_14025v1_legacy_claim12_measurements.csv", True, "EX-C1 per-cell trace"),
    ExpectedFile("external audit", "artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2304_08814v2_claim5_measurements.csv", True, "EX-C3 per-cell trace"),
    ExpectedFile("external audit", "artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim4_measurements.csv", True, "EX-C5 per-cell trace"),
    ExpectedFile("external audit", "artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2202_14025v1_legacy_claim6_measurements.csv", True, "EX-C6 per-cell trace"),
    ExpectedFile("external audit", "artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim3_measurements.csv", True, "EX-C7 per-cell trace"),
    ExpectedFile("external audit", "artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim1_measurements.csv", True, "EX-C8 per-cell trace"),
    ExpectedFile("canonical", "paper/output/figures/section5/canonical24_forest_data.csv", True, "canonical 24 Wilson results"),
    ExpectedFile("controlled validation", "data/synthetic/calibration_results.csv", True, "Wilson coverage calibration"),
    ExpectedFile("controlled validation", "output/paper/icse_pack/derived/ANALYSIS/synthetic_control_sanity.csv", True, "original synthetic controls"),
    ExpectedFile("controlled validation", "output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv", True, "expanded synthetic reversed controls"),
    ExpectedFile("controlled validation", "output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv", True, "supporting chemistry slice"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/l1_within_qiskit_diagnostic_data.csv", True, "RQ3 L1Q row-level grid"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/l1_within_qiskit_diagnostic_summary.csv", True, "RQ3 L1Q summary"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/l2_sampling_diagnostic_data.csv", True, "RQ3 L2 row-level grid"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/l2_sampling_diagnostic_summary.csv", True, "RQ3 L2 summary"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/l3_noise_diagnostic_data.csv", True, "RQ3 six-regime L3 row-level grid"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/l3_noise_diagnostic_summary.csv", True, "RQ3 six-regime L3 summary"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/algo_diagnostic_data.csv", True, "RQ3 ALGO row-level grid"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/algo_diagnostic_summary.csv", True, "RQ3 ALGO summary"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/combined_layer_diagnostic_data.csv", True, "RQ3 combined row-level grid"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/combined_layer_diagnostic_summary.csv", True, "RQ3 combined summary"),
    ExpectedFile("controlled validation", "paper/output/figures/section5/rq3_controlled_validation_summary.csv", True, "RQ3 five-diagnostic aggregate"),
    ExpectedFile("robustness", "paper/output/figures/section5/cluster_bootstrap_47.csv", True, "manuscript-facing cluster bootstrap robustness (47-row: 24 canonical + 8 external + 15 RQ3 suite)"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/expanded_seed_sensitivity.csv", True, "Tier-1 seed/budget expansion (N=80..320; EX-C7 0/320)"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/RECONSTRUCTION_README.md", True, "validated Tier-1 reconstruction method and evidence boundary"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/n_provenance_manifest.csv", True, "predeclared N factorization and expandable-axis provenance"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/reconstruction_gate_report.csv", True, "four-record 80/80 reconstruction gate"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/reconstructed_vs_locked_diff.csv", True, "empty reconstruction mismatch ledger"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_driver.py", True, "Tier-1 reconstruction/consolidation driver"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C3_0_19.jsonl", True, "EX-C3 reconstruction cells through N=320"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C5_0_19.jsonl", True, "EX-C5 reconstruction cells through N=320"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C7_0_19.jsonl", True, "EX-C7 reconstruction cells through N=320"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C6_0_19.jsonl", True, "EX-C6 reconstruction cells through N=80"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C6_20_39.jsonl", True, "EX-C6 reconstruction cells through N=160"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C6_40_59.jsonl", True, "EX-C6 reconstruction cells through N=240"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/recon_raw/EX-C6_60_79.jsonl", True, "EX-C6 reconstruction cells through N=320"),
    ExpectedFile("robustness", "paper/output/figures/section5/sensitivity_summary.csv", True, "tau/N/toggle sensitivity"),
    ExpectedFile("robustness", "paper/output/figures/section5/practical_stability_results_table.csv", True, "practical stability table data"),
    ExpectedFile("robustness", "paper/output/figures/section5/baseline_diagnostic_fallback.csv", True, "baseline diagnostic fallback"),
    ExpectedFile("robustness", "paper/output/figures/section5/perturbation_diagnostic.md", True, "matched-block perturbation diagnostic"),
    ExpectedFile("robustness", "paper/output/figures/section5/variance_decomposition_values.csv", True, "variance attribution summary"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/canonical24_forest.pdf", True, "Figure: canonical 24 forest plot"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/external_forest.pdf", True, "Figure: external forest plot"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/two_tier_barrier.pdf", True, "Figure: two-tier barrier"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/field_protocol_summary.csv", True, "Table III source data"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/field_protocol_summary.tex", True, "Table III LaTeX"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/per_claim_external_audit.csv", True, "Table IV source data"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/per_claim_external_audit.tex", True, "Table IV LaTeX"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/materialization_funnel.csv", True, "materialization funnel source data"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/materialization_funnel.tex", True, "materialization funnel LaTeX"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/practical_stability_results.tex", True, "practical stability LaTeX"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/baseline_diagnostic_fallback.tex", True, "baseline diagnostic LaTeX"),
    ExpectedFile("figures/tables", "paper/output/figures/section5/per_claim_perturbations.tex", True, "perturbation specification LaTeX"),
    ExpectedFile("scripts", "artifact/scripts/check_artifact_files.py", True, "file availability checker"),
    ExpectedFile("scripts", "artifact/scripts/check_headline_numbers.py", True, "headline number checker"),
    ExpectedFile("scripts", "artifact/scripts/build_rq1_claim_decisions.py", True, "row-level final RQ1 registry verifier/generator"),
    ExpectedFile("scripts", "artifact/scripts/check_markdown_links.py", True, "Markdown link checker"),
    ExpectedFile("scripts", "artifact/scripts/check_rq4_robustness.py", True, "RQ4 robustness alignment checker"),
    ExpectedFile("scripts", "artifact/data/corpus/coding_validity/recompute_agreement.py", True, "coding-validity agreement recompute"),
    ExpectedFile("scripts", "artifact/external_audit/tier1_robustness/tier1_robustness_analysis.py", True, "Tier-1 robustness analysis (re-runnable)"),
]


def check_files() -> tuple[list[tuple[ExpectedFile, bool]], int, int]:
    rows: list[tuple[ExpectedFile, bool]] = []
    missing_required = 0
    missing_optional = 0
    for item in EXPECTED_FILES:
        # Self-contained fallback: prefer the repo-root source; if absent (e.g. only
        # artifact/ was shipped), accept the vendored copy under artifact/results/.
        exists = (REPO_ROOT / item.path).exists() or (REPO_ROOT / "artifact" / "results" / item.path).exists()
        rows.append((item, exists))
        if not exists and item.required:
            missing_required += 1
        if not exists and not item.required:
            missing_optional += 1
    return rows, missing_required, missing_optional


def write_report(rows: list[tuple[ExpectedFile, bool]], missing_required: int, missing_optional: int) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(rows)
    found = sum(1 for _, exists in rows if exists)
    lines = [
        "# Artifact File Check",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Summary: {found}/{total} expected files found; {missing_required} required missing; {missing_optional} optional missing.",
        "",
        "| Category | Path | Required | Status | Purpose |",
        "|---|---|---:|---|---|",
    ]
    for item, exists in rows:
        status = "FOUND" if exists else "MISSING"
        lines.append(f"| {item.category} | `{item.path}` | {item.required} | {status} | {item.purpose} |")
    lines.append("")
    if missing_required:
        lines.append("Required files are missing. See rows marked `MISSING` above.")
    else:
        lines.append("All required artifact files are present.")
    REPORT_PATH.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Opt in to writing artifact/outputs/reports/artifact_file_check.md. "
        "The default verification mode is read-only.",
    )
    args = parser.parse_args(argv)

    rows, missing_required, missing_optional = check_files()
    found = sum(1 for _, exists in rows if exists)
    total = len(rows)

    if not args.write_report:
        # Concise default: write nothing.
        print(
            f"[artifact-check] {found}/{total} files present; "
            f"{missing_required} required missing; {missing_optional} optional missing."
        )
        for item, exists in rows:
            if not exists and item.required:
                print(f"  MISSING (required): {item.path}")
    else:
        write_report(rows, missing_required, missing_optional)
        for item, exists in rows:
            prefix = "[PASS]" if exists else ("[MISSING]" if item.required else "[OPTIONAL-MISSING]")
            print(f"{prefix} {item.path}")
        print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 1 if missing_required else 0


if __name__ == "__main__":
    sys.exit(main())
