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


_TRUE_STRINGS = frozenset({"true", "1", "yes"})
_FALSE_STRINGS = frozenset({"false", "0", "no"})


def _parse_boolean(value: Any) -> bool:
    """Parse an unambiguous boolean value or reject it.

    Artifact evidence commonly arrives through CSV/YAML, where booleans may be
    strings.  Calling ``bool(value)`` is unsafe because ``bool("False")`` is
    true in Python.
    """

    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE_STRINGS:
            return True
        if normalized in _FALSE_STRINGS:
            return False
    raise ValueError(f"ambiguous boolean evidence value: {value!r}")


def _parse_boolean_sequence(values: Sequence[Any]) -> tuple[bool, ...]:
    return tuple(_parse_boolean(value) for value in values)


def _validate_scalar_counts(successes: int, total: int) -> None:
    if total <= 0:
        raise ValueError("scalar directional check requires total > 0")
    if successes < 0 or successes > total:
        raise ValueError("successes must satisfy 0 <= successes <= total")


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
            outcomes = _parse_boolean_sequence(artifact_inputs["outcomes"])
            total = len(outcomes)
            successes = sum(1 for v in outcomes if v)
        else:
            successes = int(artifact_inputs["successes"])
            total = int(artifact_inputs["total"])

        if total == 0:
            return RelationAuditResult(
                verdict="INFEASIBLE",
                relation_type=self.relation_type,
                evidence_boundary="scalar directional check requires total > 0",
                materialization_status=MaterializationStatus.INFEASIBLE,
                provenance_files=materialization.artifact_provenance,
            )
        _validate_scalar_counts(successes, total)

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
        outcomes = _parse_boolean_sequence(p["outcomes"])
        n = len(outcomes)
        k = sum(1 for v in outcomes if v)
    else:
        k = int(p["k"])
        n = int(p["n"])
    tau = float(p.get("tau", 0.95))
    confidence = float(p.get("confidence", 0.95))
    if n == 0:
        return RelationCheckOutput(
            checker_name="scalar_directional_wilson",
            outcome="Boundary",
            boundary_reason="no matched cells (N=0)",
            evidence_used=inp.evidence_object,
        )
    _validate_scalar_counts(k, n)
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
    excluded_nonpositive = 0
    if "ratios" in p:
        raw_ratios = [float(r) for r in p["ratios"]]
        ratios = [ratio for ratio in raw_ratios if ratio > 0]
        n_considered = len(raw_ratios)
        excluded_nonpositive = n_considered - len(ratios)
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
                excluded_nonpositive += 1
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

    convention = str(p.get("zero_failure_convention", p.get("convention", ""))).strip()
    if excluded_nonpositive and convention != "exclude_nonpositive":
        return RelationCheckOutput(
            checker_name="aggregate_relation",
            outcome="Boundary",
            boundary_reason=(
                "non-positive aggregate rows require the locked "
                "zero_failure_convention='exclude_nonpositive'"
            ),
            evidence_used=inp.evidence_object,
        )

    agg = _geomean(ratios)
    condition = str(p.get("preservation", "ratio_lt_1"))
    if condition == "ratio_lt_1":
        preserved = agg < 1.0
    elif condition == "ratio_gt_1":
        preserved = agg > 1.0
    else:
        raise ValueError(f"unsupported aggregate preservation condition: {condition!r}")
    diagnostic = p.get("row_level_diagnostic")  # e.g. {"k":16,"n":22} (separate from verdict)
    return RelationCheckOutput(
        checker_name="aggregate_relation",
        outcome="Preserved" if preserved else "NotPreserved",
        quantitative_statistic={
            "aggregation": aggregation,
            "aggregate_value": agg,
            "rows_used": len(ratios),
            "rows_considered": n_considered,
            "rows_excluded_nonpositive": excluded_nonpositive,
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
    flags = _parse_boolean_sequence(p.get("concordant", []))
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
    if rule == "all_concordant":
        concordant = k == n
    elif rule == "min_concordant":
        minimum = int(p.get("min_concordant", n))
        if minimum < 0 or minimum > n:
            raise ValueError("min_concordant must satisfy 0 <= value <= total")
        concordant = k >= minimum
    else:
        raise ValueError(f"unsupported crossover concordance rule: {rule!r}")
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
        if not order:
            raise ValueError("equal_or_better requires an explicit category_order")
        if observed not in order or expected not in order:
            raise ValueError("observed and expected categories must both appear in category_order")
        preserved = order.index(observed) <= order.index(expected)
    else:
        raise ValueError(f"unsupported categorical relation: {relation!r}")
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
