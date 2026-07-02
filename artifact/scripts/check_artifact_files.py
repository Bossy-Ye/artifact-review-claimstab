#!/usr/bin/env python3
"""Check that the reviewer-facing CLAIMSTAB-QC artifact files exist.

This script is intentionally lightweight: it does not regenerate experiments
or mutate locked result files. It verifies file availability and writes a
Markdown report for artifact reviewers.
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
    ExpectedFile("artifact docs", "artifact/ARTIFACT_MANIFEST.md", True, "top-level artifact map"),
    ExpectedFile("artifact docs", "artifact/PAPER_CLAIMS_TO_EVIDENCE.md", True, "paper claim to evidence mapping"),
    ExpectedFile("artifact docs", "artifact/README.md", True, "reviewer entry point + verification commands"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/paper_list_250_screened.csv", True, "119 included papers from screened corpus"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/inclusion_exclusion_criteria.md", True, "corpus selection protocol"),
    ExpectedFile("field corpus", "artifact/field_study/corpus/search_protocol.md", True, "Google Scholar search-and-screen protocol bridge note; normalized provenance"),
    ExpectedFile("field corpus", "artifact/field_study/coding_protocol/coding_guide.md", True, "field-coding guide"),
    ExpectedFile("field corpus", "artifact/field_study/coding_protocol/claim_unitization_rules.md", True, "claim unitization rules"),
    ExpectedFile("field corpus", "artifact/field_study/claims/extraction_worksheet_template.csv", True, "worksheet template"),
    ExpectedFile("field corpus", "artifact/field_study/claims/extracted_claims_457.csv", True, "457 accepted claims with evidence fields"),
    ExpectedFile("field corpus", "artifact/field_study/rq1_materialization_barrier_taxonomy.csv", True, "RQ1 materialization disposition (Table III): 79 = 53 auditable + 26 boundary"),
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
    ExpectedFile("materialization", "artifact/external_audit/feasibility_notes/qvans_high_risk_review.md", True, "QVAns high-risk final review"),
    ExpectedFile("materialization", "artifact/external_audit/feasibility_notes/qvans_feasibility_table.csv", True, "QVAns feasibility table"),
    ExpectedFile("external audit", "artifact/external_audit/mapping/source_mapping_anonymized.csv", True, "EX-C1..EX-C8 source mapping"),
    ExpectedFile("external audit", "artifact/external_audit/feasibility_notes/failed_external_claims.md", True, "blocked/failed external claims"),
    ExpectedFile("external audit", "paper/output/figures/section5/external_forest_data.csv", True, "8 external audit Wilson results"),
    ExpectedFile("external audit", "paper/output/figures/section5/per_claim_perturbations.csv", True, "external perturbation specification"),
    ExpectedFile("canonical", "paper/output/figures/section5/canonical24_forest_data.csv", True, "canonical 24 Wilson results"),
    ExpectedFile("controlled validation", "data/synthetic/calibration_results.csv", True, "Wilson coverage calibration"),
    ExpectedFile("controlled validation", "output/paper/icse_pack/derived/ANALYSIS/synthetic_control_sanity.csv", True, "original synthetic controls"),
    ExpectedFile("controlled validation", "output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv", True, "expanded synthetic reversed controls"),
    ExpectedFile("controlled validation", "output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv", True, "supporting chemistry slice"),
    ExpectedFile("robustness", "paper/output/figures/section5/cluster_bootstrap_47.csv", True, "manuscript-facing cluster bootstrap robustness (47-row: 24 canonical + 8 external + 15 RQ3 suite)"),
    ExpectedFile("robustness", "artifact/external_audit/budget_sensitivity/expanded_seed_sensitivity.csv", True, "Tier-1 seed/budget expansion (N=80..320; EX-C7 0/320)"),
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
        "--no-write",
        action="store_true",
        help="Verify file availability only; do not create or modify any report files "
        "(leaves artifact/outputs/reports/ untouched). Reviewer-safe.",
    )
    args = parser.parse_args(argv)

    rows, missing_required, missing_optional = check_files()
    found = sum(1 for _, exists in rows if exists)
    total = len(rows)

    if args.no_write:
        # Concise summary only; write nothing.
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
