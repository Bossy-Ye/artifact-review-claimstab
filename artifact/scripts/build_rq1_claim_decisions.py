#!/usr/bin/env python3
"""Build and verify the derived row-level RQ1 decision crosscheck.

The raw 457-row relation-schema flags predate the documented source-grounded
crosscheck.  This script applies the 16-row outcome-blind decision overlay,
derives the corrected funnel decisions, and verifies both the decision crosscheck
and paper rollup.  The paper-facing accepted-claim authority remains the corrected
count and source-grounded adjudication tables.  This script does not inspect source
outcomes or run quantum experiments.
"""

from __future__ import annotations

import argparse
import csv
import io
from collections import Counter
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1]
RAW_CLAIMS = ARTIFACT / "field_study/claims/extracted_claims_457.csv"
RAW_FLAGS = ARTIFACT / "field_study/claims/relation_schema_rq1_flags.csv"
CROSSCHECK = ARTIFACT / "headline_count_final_crosscheck_decisions.csv"
ADJUDICATION = ARTIFACT / "source_grounded_claim_adjudication.csv"
SCREENED_PAPERS = ARTIFACT / "field_study/corpus/paper_list_250_screened.csv"
CLAIM_OUTPUT = ARTIFACT / "field_study/claims/rq1_claim_decisions_457.csv"
PAPER_OUTPUT = ARTIFACT / "field_study/corpus/final_rq1_paper_registry_119.csv"

CLAIM_FIELDS = (
    "claim_id",
    "paper_id",
    "paradigm",
    "confidence",
    "final_accepted_comparative_claim",
    "final_claim_card_specifiable",
    "final_relation_family",
    "final_scalar_directional",
    "final_planning_feasible",
    "final_scalar_oriented_planning",
    "final_perturbation_audit_candidate",
    "final_verification_only",
    "final_materialized_rq2",
    "final_tier",
    "decision_source",
    "source_evidence_status",
    "source_location",
    "decision_note",
)

PAPER_FIELDS = (
    "paper_id",
    "title",
    "screening_decision",
    "final_accepted_claim_count",
    "contributes_accepted_claims",
)

RELATION_OVERRIDES = {
    "ext_2202_14025v1_legacy_claim5": "categorical_or_equality",
    "ext_2202_14025v1_legacy_claim11": "multi_objective",
    "ext_2305_03390v1_claim1": "multi_objective",
    "ext_2309_01028v2_claim4": "multi_objective",
    "ext_2409_15055v2_claim2": "crossover_or_regional",
    "ext_2411_00518v2_claim2": "crossover_or_regional",
}

EXPECTED_COUNTS = {
    "accepted": 455,
    "specifiable": 175,
    "scalar": 145,
    "planning": 93,
    "scalar_planning": 79,
    "perturbation_candidates": 77,
    "verification_only": 2,
    "materialized": 8,
}

EXPECTED_RELATION_COUNTS = {
    "scalar_directional": 145,
    "multi_objective": 26,
    "categorical_or_equality": 2,
    "crossover_or_regional": 2,
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"ambiguous boolean value: {value!r}")


def as_text(value: bool) -> str:
    return "true" if value else "false"


def index_unique(rows: list[dict[str, str]], key: str, source: Path) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in indexed:
            raise ValueError(f"duplicate {key}={value!r} in {source}")
        indexed[value] = row
    return indexed


def normalized_previous_relation(value: str, scalar: bool, specifiable: bool) -> str:
    if not specifiable:
        return "not_specifiable"
    if scalar:
        return "scalar_directional"
    mapping = {
        "multi_objective": "multi_objective",
        "categorical_equal_or_better": "categorical_or_equality",
        "equality": "categorical_or_equality",
        "crossover_regional": "crossover_or_regional",
    }
    if value not in mapping:
        raise ValueError(f"missing relation family for a specifiable non-scalar row: {value!r}")
    return mapping[value]


def build_claim_registry() -> list[dict[str, str]]:
    claims = read_rows(RAW_CLAIMS)
    flags = index_unique(read_rows(RAW_FLAGS), "claim_id", RAW_FLAGS)
    decisions = index_unique(read_rows(CROSSCHECK), "claim_id", CROSSCHECK)
    adjudications = index_unique(read_rows(ADJUDICATION), "claim_id", ADJUDICATION)

    if len(claims) != 457 or set(flags) != {row["claim_id"] for row in claims}:
        raise ValueError("raw claim and relation-flag registries must contain the same 457 claim IDs")
    if len(decisions) != 16:
        raise ValueError("the final crosscheck overlay must contain exactly 16 decisions")

    output: list[dict[str, str]] = []
    for claim in claims:
        claim_id = claim["claim_id"]
        raw = flags[claim_id]
        decision = decisions.get(claim_id)
        adjudication = adjudications.get(claim_id, {})

        accepted = parse_bool(raw["accepted"])
        specifiable = parse_bool(raw["specifiable_relation_schema"])
        scalar = parse_bool(raw["scalar_directional"])
        planning = parse_bool(raw["planning_feasible"])
        scalar_planning = parse_bool(raw["scalar_oriented_planning"])
        perturbation = parse_bool(raw["perturbation_audit_candidate"])

        if decision:
            specifiable = parse_bool(decision["final_label_claim_card_specifiable"])
            scalar = parse_bool(decision["final_label_scalar_directional"])
            planning = parse_bool(decision["final_label_planning_feasible"])
            if int(decision["delta_accepted_claim_count"]):
                accepted = False
            if int(decision["delta_78"]) == 1:
                scalar_planning = True
            if claim_id == "ext_2309_01028v2_claim5":
                perturbation = True

        if not (accepted and scalar and planning):
            scalar_planning = False

        previous_relation = adjudication.get("previous_relation_type", "")
        if claim_id in RELATION_OVERRIDES:
            relation = RELATION_OVERRIDES[claim_id]
        else:
            relation = normalized_previous_relation(previous_relation, scalar, specifiable)

        evidence_status = adjudication.get("source_evidence_status", "")
        source_location = adjudication.get("source_location", "") or claim["claim_location"]
        output.append(
            {
                "claim_id": claim_id,
                "paper_id": claim["arxiv_id"],
                "paradigm": claim["paradigm"],
                "confidence": claim["confidence"],
                "final_accepted_comparative_claim": as_text(accepted),
                "final_claim_card_specifiable": as_text(specifiable),
                "final_relation_family": relation,
                "final_scalar_directional": as_text(scalar),
                "final_planning_feasible": as_text(planning),
                "final_scalar_oriented_planning": as_text(scalar_planning),
                "final_perturbation_audit_candidate": as_text(perturbation),
                "final_verification_only": raw["verification_only"].lower(),
                "final_materialized_rq2": raw["materialized_rq2"].lower(),
                "final_tier": raw["tier"],
                "decision_source": (
                    "headline_count_final_crosscheck_decisions.csv"
                    if decision
                    else "relation_schema_rq1_flags.csv"
                ),
                "source_evidence_status": evidence_status or "raw_extraction_record",
                "source_location": source_location,
                "decision_note": decision["notes"] if decision else raw["notes"],
            }
        )

    validate_claim_registry(output)
    return output


def validate_claim_registry(rows: list[dict[str, str]]) -> None:
    if len(rows) != 457 or len({row["claim_id"] for row in rows}) != 457:
        raise ValueError("decision crosscheck must contain 457 unique candidate rows")

    selectors = {
        "accepted": "final_accepted_comparative_claim",
        "specifiable": "final_claim_card_specifiable",
        "scalar": "final_scalar_directional",
        "planning": "final_planning_feasible",
        "scalar_planning": "final_scalar_oriented_planning",
        "perturbation_candidates": "final_perturbation_audit_candidate",
        "verification_only": "final_verification_only",
        "materialized": "final_materialized_rq2",
    }
    actual = {
        name: sum(parse_bool(row[field]) for row in rows)
        for name, field in selectors.items()
    }
    if actual != EXPECTED_COUNTS:
        raise ValueError(f"final RQ1 funnel mismatch: expected {EXPECTED_COUNTS}, got {actual}")

    for row in rows:
        accepted = parse_bool(row["final_accepted_comparative_claim"])
        specifiable = parse_bool(row["final_claim_card_specifiable"])
        scalar = parse_bool(row["final_scalar_directional"])
        planning = parse_bool(row["final_planning_feasible"])
        scalar_planning = parse_bool(row["final_scalar_oriented_planning"])
        perturbation = parse_bool(row["final_perturbation_audit_candidate"])
        verification = parse_bool(row["final_verification_only"])
        materialized = parse_bool(row["final_materialized_rq2"])
        expected_intersection = accepted and scalar and planning
        if scalar_planning != expected_intersection:
            raise ValueError(f"{row['claim_id']}: scalar-planning flag is not the final intersection")
        if (scalar or planning or materialized) and not (accepted and specifiable):
            raise ValueError(f"{row['claim_id']}: downstream RQ1 flag escapes accepted/specifiable set")
        if perturbation and verification:
            raise ValueError(f"{row['claim_id']}: perturbation and verification-only flags overlap")
        if scalar_planning != (perturbation or verification):
            raise ValueError(f"{row['claim_id']}: final 79-set is not partitioned into 77+2")
        if materialized and not perturbation:
            raise ValueError(f"{row['claim_id']}: materialized record is not a perturbation candidate")
        expected_relation = "not_specifiable" if not specifiable else row["final_relation_family"]
        if row["final_relation_family"] != expected_relation:
            raise ValueError(f"{row['claim_id']}: non-specifiable row has a relation family")
        if scalar and row["final_relation_family"] != "scalar_directional":
            raise ValueError(f"{row['claim_id']}: scalar flag and relation family disagree")

    relation_counts = Counter(
        row["final_relation_family"]
        for row in rows
        if parse_bool(row["final_claim_card_specifiable"])
    )
    if dict(relation_counts) != EXPECTED_RELATION_COUNTS:
        raise ValueError(
            f"final represented-relation distribution mismatch: "
            f"expected {EXPECTED_RELATION_COUNTS}, got {dict(relation_counts)}"
        )
    accepted_rows = [row for row in rows if parse_bool(row["final_accepted_comparative_claim"])]
    confidence_counts = Counter(row["confidence"] for row in accepted_rows)
    if confidence_counts != Counter({"HIGH": 343, "MEDIUM": 112}):
        raise ValueError(f"final accepted-confidence distribution mismatch: {confidence_counts}")
    paradigm_counts = Counter(row["paradigm"] for row in accepted_rows)
    if paradigm_counts != Counter({"compilation": 142, "variational": 313}):
        raise ValueError(f"final accepted-paradigm distribution mismatch: {paradigm_counts}")


def build_paper_registry(claim_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    accepted_counts = Counter(
        row["paper_id"]
        for row in claim_rows
        if parse_bool(row["final_accepted_comparative_claim"])
    )
    included = [
        row for row in read_rows(SCREENED_PAPERS)
        if row["screening_decision"].strip().lower() == "include"
    ]
    if len(included) != 119:
        raise ValueError(f"expected 119 screened-in papers, found {len(included)}")
    if len({row["arxiv_id"] for row in included}) != 119:
        raise ValueError("screened-in paper identifiers must be unique")
    output = [
        {
            "paper_id": row["arxiv_id"],
            "title": row["title"],
            "screening_decision": "include",
            "final_accepted_claim_count": str(accepted_counts[row["arxiv_id"]]),
            "contributes_accepted_claims": as_text(accepted_counts[row["arxiv_id"]] > 0),
        }
        for row in included
    ]
    if sum(int(row["final_accepted_claim_count"]) for row in output) != 455:
        raise ValueError("paper registry must account for all 455 accepted claims")
    if sum(parse_bool(row["contributes_accepted_claims"]) for row in output) != 118:
        raise ValueError("expected 118 of 119 screened-in papers to contribute accepted claims")
    return output


def render_csv(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def verify_or_write(path: Path, content: str, write: bool) -> None:
    if write:
        path.write_text(content, encoding="utf-8")
        return
    if not path.exists():
        raise FileNotFoundError(f"missing generated registry: {path.relative_to(ARTIFACT.parent)}")
    if path.read_text(encoding="utf-8") != content:
        raise ValueError(
            f"generated registry is stale: {path.relative_to(ARTIFACT.parent)}; rerun with --write"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace committed registry outputs")
    args = parser.parse_args()

    claims = build_claim_registry()
    papers = build_paper_registry(claims)
    verify_or_write(CLAIM_OUTPUT, render_csv(claims, CLAIM_FIELDS), args.write)
    verify_or_write(PAPER_OUTPUT, render_csv(papers, PAPER_FIELDS), args.write)

    relation_counts = Counter(
        row["final_relation_family"]
        for row in claims
        if parse_bool(row["final_claim_card_specifiable"])
    )
    print("RQ1 decision crosscheck verified: 457 candidates -> 455 accepted; 119-paper corpus (118 contributing)")
    print("Funnel: 175 represented; 145 scalar; 93 planning; 79 scalar-planning; 8 Tier-1")
    print("Represented relation families:", dict(relation_counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
