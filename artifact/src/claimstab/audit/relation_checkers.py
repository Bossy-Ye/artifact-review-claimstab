"""Relation-specific checker interfaces and scalar Wilson adapter."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from claimstab.inference.policies import wilson_interval

from .relations import (
    MaterializationStatus,
    RelationAuditResult,
    RelationChecker,
    RelationType,
    check_relation_materialization,
)
from .verdicts import classify_direction_preservation


class ScalarDirectionalWilsonChecker:
    """Wrap the existing scalar direction-preservation Wilson pipeline."""

    relation_type = RelationType.SCALAR_DIRECTIONAL

    def check(self, card: Any, artifact_inputs: Mapping[str, Any]) -> RelationAuditResult:
        materialization = check_relation_materialization(card, relation_type=self.relation_type)
        if not materialization.feasible:
            return RelationAuditResult(
                verdict="INFEASIBLE",
                relation_type=self.relation_type,
                evidence_boundary=materialization.evidence_boundary,
                materialization_status=materialization.status,
                provenance_files=materialization.artifact_provenance,
            )

        if "outcomes" in artifact_inputs:
            outcomes: Sequence[bool] = tuple(bool(v) for v in artifact_inputs["outcomes"])
            total = len(outcomes)
            successes = sum(1 for v in outcomes if v)
        else:
            successes = int(artifact_inputs["successes"])
            total = int(artifact_inputs["total"])

        if total <= 0:
            return RelationAuditResult(
                verdict="INFEASIBLE",
                relation_type=self.relation_type,
                evidence_boundary="scalar directional check requires total > 0",
                materialization_status=MaterializationStatus.INFEASIBLE,
                provenance_files=materialization.artifact_provenance,
            )

        confidence = float(artifact_inputs.get("confidence", 0.95))
        tau = float(artifact_inputs.get("tau", 0.95))
        lower, upper = wilson_interval(successes, total, confidence=confidence)
        verdict = classify_direction_preservation(lower, upper, tau=tau).value
        return RelationAuditResult(
            verdict=verdict,
            relation_type=self.relation_type,
            evidence_boundary=str(artifact_inputs.get("evidence_boundary", "")),
            materialization_status=MaterializationStatus.MATERIALIZED,
            provenance_files=tuple(artifact_inputs.get("provenance_files", ())),
            sensitivity_summary=artifact_inputs.get("sensitivity_summary"),
            statistics={
                "successes": successes,
                "total": total,
                "preservation_rate": successes / total,
                "wilson_lower": lower,
                "wilson_upper": upper,
                "confidence": confidence,
                "tau": tau,
            },
        )


def get_relation_checker(relation_type: RelationType | str) -> RelationChecker:
    """Return the checker for a relation type currently implemented in code."""

    rtype = relation_type if isinstance(relation_type, RelationType) else RelationType(str(relation_type))
    if rtype is RelationType.SCALAR_DIRECTIONAL:
        return ScalarDirectionalWilsonChecker()
    raise NotImplementedError(f"no relation checker implemented for {rtype.value}")


# ---------------------------------------------------------------------------
# Unified minimal relation-checker interface (RQ2 alignment)
#
# One conceptual interface shared by every checker:
#     RelationCheckInput -> check(...) -> RelationCheckOutput
#
# The loop these checkers close is:
#     claim card -> source-defined evidence object -> relation-specific checker
#       -> scoped preservation outcome -> explanation/boundary report
#
# These functions are pure: they consume already-recorded evidence (k/N,
# source-table rows, per-device concordance, blocker metadata) and recompute the
# scoped outcome. They do NOT run new audit experiments.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RelationCheckInput:
    """Common input shape for every relation-specific checker."""

    relation_type: str
    claim_id: str
    evidence_object: str = ""
    scope: str = ""
    environment: str = ""
    params: Mapping[str, Any] = field(default_factory=dict)
    boundary_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RelationCheckOutput:
    """Common output shape for every relation-specific checker."""

    checker_name: str
    outcome: str
    quantitative_statistic: Any = None
    diagnostic_statistic: Any = None
    evidence_used: str = ""
    boundary_reason: str | None = None
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "checker_name": self.checker_name,
            "outcome": self.outcome,
            "quantitative_statistic": self.quantitative_statistic,
            "diagnostic_statistic": self.diagnostic_statistic,
            "evidence_used": self.evidence_used,
            "boundary_reason": self.boundary_reason,
            "notes": self.notes,
        }


def _geomean(values: Sequence[float]) -> float:
    """Geometric mean of strictly-positive values."""

    vals = [float(v) for v in values]
    if not vals or any(v <= 0 for v in vals):
        raise ValueError("geometric mean requires a non-empty set of positive values")
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


# 1. Scalar-directional Wilson checker -------------------------------------

def scalar_directional_wilson_check(inp: RelationCheckInput) -> RelationCheckOutput:
    """Wilson direction-preservation over matched cells (k of N preserved)."""

    p = inp.params
    if "outcomes" in p:
        outcomes = [bool(v) for v in p["outcomes"]]
        n = len(outcomes)
        k = sum(1 for v in outcomes if v)
    else:
        k = int(p["k"])
        n = int(p["n"])
    tau = float(p.get("tau", 0.95))
    confidence = float(p.get("confidence", 0.95))
    if n <= 0:
        return RelationCheckOutput(
            checker_name="scalar_directional_wilson",
            outcome="Boundary",
            boundary_reason="no matched cells (N=0)",
            evidence_used=inp.evidence_object,
        )
    lower, upper = wilson_interval(successes=k, total=n, confidence=confidence)
    status = classify_direction_preservation(lower, upper, tau=tau)
    return RelationCheckOutput(
        checker_name="scalar_directional_wilson",
        outcome=status.value,
        quantitative_statistic={
            "k": k,
            "n": n,
            "rate": k / n,
            "wilson_lower": lower,
            "wilson_upper": upper,
            "tau": tau,
        },
        evidence_used=inp.evidence_object,
        notes=inp.params.get("notes", ""),
    )


# 2. Aggregate relation checker --------------------------------------------

def aggregate_relation_check(inp: RelationCheckInput) -> RelationCheckOutput:
    """Aggregate (e.g. geomean) preservation over a source-defined table.

    Formal verdict comes from recomputing the aggregate relation over the
    source rows. A row-level Wilson split may be passed as a diagnostic only;
    it never sets the aggregate verdict.
    """

    p = inp.params
    aggregation = str(p.get("aggregation", "geomean_cost_ratio"))
    rows = p.get("rows")
    ratios: list[float]
    if "ratios" in p:
        ratios = [float(r) for r in p["ratios"] if float(r) > 0]
        n_considered = len(p["ratios"])
    elif rows is not None:
        # cost-ratio convention: geomean of c_a / c_b over rows where both > 0
        ratios = []
        n_considered = 0
        for row in rows:
            n_considered += 1
            ca = float(row.get("c_a", row.get("c_olsq", 0.0)))
            cb = float(row.get("c_b", row.get("c_tket", 0.0)))
            if ca > 0 and cb > 0:
                ratios.append(ca / cb)
    else:
        return RelationCheckOutput(
            checker_name="aggregate_relation",
            outcome="Boundary",
            boundary_reason="no source rows or ratios provided to recompute the aggregate",
            evidence_used=inp.evidence_object,
        )

    if not ratios:
        return RelationCheckOutput(
            checker_name="aggregate_relation",
            outcome="Boundary",
            boundary_reason="no usable rows (all zero/degenerate); aggregate not recomputable",
            evidence_used=inp.evidence_object,
            notes=str(p.get("convention", "")),
        )

    agg = _geomean(ratios)
    condition = str(p.get("preservation", "ratio_lt_1"))
    preserved = agg < 1.0 if condition == "ratio_lt_1" else agg > 1.0
    diagnostic = p.get("row_level_diagnostic")  # e.g. {"k":16,"n":22} (separate from verdict)
    return RelationCheckOutput(
        checker_name="aggregate_relation",
        outcome="Preserved" if preserved else "NotPreserved",
        quantitative_statistic={
            "aggregation": aggregation,
            "aggregate_value": agg,
            "rows_used": len(ratios),
            "rows_considered": n_considered,
            "preservation_condition": condition,
        },
        diagnostic_statistic=diagnostic,
        evidence_used=inp.evidence_object,
        notes=str(p.get("convention", "")),
    )


# 3. Crossover / regional checker ------------------------------------------

def crossover_regional_check(inp: RelationCheckInput) -> RelationCheckOutput:
    """Region/device-pattern (e.g. crossover) preservation by concordance rule."""

    p = inp.params
    flags = [bool(v) for v in p.get("concordant", [])]
    rule = str(p.get("rule", "all_concordant"))
    n = len(flags)
    if n == 0:
        return RelationCheckOutput(
            checker_name="crossover_regional",
            outcome="Boundary",
            boundary_reason="no region/device outcomes to evaluate concordance",
            evidence_used=inp.evidence_object,
        )
    k = sum(1 for v in flags if v)
    concordant = (k == n) if rule == "all_concordant" else (k >= int(p.get("min_concordant", n)))
    return RelationCheckOutput(
        checker_name="crossover_regional",
        outcome="Concordant" if concordant else "Discordant",
        quantitative_statistic={"concordant": k, "total": n, "rule": rule},
        evidence_used=inp.evidence_object,
        notes=str(p.get("notes", "")),
    )


# 4. Categorical checker ----------------------------------------------------

def categorical_check(inp: RelationCheckInput) -> RelationCheckOutput:
    """Equality / equal-or-better / same-category preservation."""

    p = inp.params
    expected = p.get("expected_category")
    observed = p.get("observed_category")
    if observed is None or expected is None:
        return RelationCheckOutput(
            checker_name="categorical",
            outcome="Boundary",
            boundary_reason="missing expected or observed category record",
            evidence_used=inp.evidence_object,
        )
    relation = str(p.get("relation", "equal"))
    if relation == "equal":
        preserved = observed == expected
    elif relation == "equal_or_better":
        order = list(p.get("category_order", []))  # better -> worse
        preserved = order.index(observed) <= order.index(expected) if order else observed == expected
    else:
        preserved = observed == expected
    return RelationCheckOutput(
        checker_name="categorical",
        outcome="Preserved" if preserved else "NotPreserved",
        quantitative_statistic={"expected": expected, "observed": observed, "relation": relation},
        evidence_used=inp.evidence_object,
        notes=str(p.get("notes", "")),
    )


# 5. Boundary checker -------------------------------------------------------

def boundary_check(inp: RelationCheckInput) -> RelationCheckOutput:
    """Formal no-verdict outcome for under-materialized or inconsistent evidence."""

    meta = {**inp.boundary_metadata, **inp.params}
    blocker = str(meta.get("blocker", "evidence object cannot be locked"))
    flag = str(meta.get("flag", "source_reporting"))  # or methodology_limitation
    return RelationCheckOutput(
        checker_name="boundary",
        outcome="No verdict",
        boundary_reason=blocker,
        evidence_used=inp.evidence_object,
        notes=f"flag={flag}; {meta.get('notes', '')}".strip("; "),
    )


_UNIFIED_CHECKERS = {
    "scalar_directional": scalar_directional_wilson_check,
    "aggregate_geomean": aggregate_relation_check,
    "aggregate_mean_curve_crossover": crossover_regional_check,
    "categorical_equal_or_better": categorical_check,
    "runtime_ratio": boundary_check,
    "complete_table_or_series": boundary_check,
    "infeasible_or_unmaterialized": boundary_check,
}


def run_relation_check(inp: RelationCheckInput) -> RelationCheckOutput:
    """Dispatch to the checker matched to the relation type."""

    rtype = inp.relation_type
    if rtype not in _UNIFIED_CHECKERS:
        raise NotImplementedError(f"no unified checker for relation type {rtype!r}")
    return _UNIFIED_CHECKERS[rtype](inp)
