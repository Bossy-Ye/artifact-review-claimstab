"""Relation-aware claim-card primitives.

The scalar Wilson pipeline remains the evaluated implementation for the current
eight external RQ2 cards. This module adds the relation vocabulary and
materialization boundary records needed for Road B and future relation-specific
checks without changing existing scalar outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol


class RelationType(str, Enum):
    """Supported source-defined comparative-relation families."""

    SCALAR_DIRECTIONAL = "scalar_directional"
    AGGREGATE_GEOMEAN = "aggregate_geomean"
    AGGREGATE_MEAN_CURVE_CROSSOVER = "aggregate_mean_curve_crossover"
    CATEGORICAL_EQUAL_OR_BETTER = "categorical_equal_or_better"
    RUNTIME_RATIO = "runtime_ratio"
    COMPLETE_TABLE_OR_SERIES = "complete_table_or_series"
    MULTI_OBJECTIVE_PARETO = "multi_objective_pareto"
    EXISTENTIAL_SUBSET = "existential_subset"
    MIXED_NEEDS_SPLIT = "mixed_needs_split"
    INFEASIBLE_OR_UNMATERIALIZED = "infeasible_or_unmaterialized"


class BoundaryVerdict(str, Enum):
    """Relation-specific boundary/result labels outside scalar S/U/R."""

    CONCORDANT = "CONCORDANT"
    NON_CONCORDANT = "NON_CONCORDANT"
    PARTIAL = "PARTIAL"
    INFEASIBLE = "INFEASIBLE"
    INDETERMINATE = "INDETERMINATE"
    CONCORDANT_RECONSTRUCTED = "CONCORDANT_RECONSTRUCTED"


class MaterializationStatus(str, Enum):
    """Whether the source/artifact exposes enough evidence for a relation check."""

    MATERIALIZED = "materialized"
    PARTIAL = "partial"
    INFEASIBLE = "infeasible"


@dataclass(frozen=True)
class RelationSpec:
    """Source-defined relation `R` in claim card C=<P,B_A,B_B,M,R>.

    Scalar directional claims preserve backward compatibility by setting
    `relation_type=scalar_directional` and `direction` to "<" or ">".
    Non-scalar cards should describe the source relation through `rule` and
    provenance fields before any outcome-bearing check runs.
    """

    relation_type: RelationType = RelationType.SCALAR_DIRECTIONAL
    direction: str | None = None
    rule: str | None = None
    aggregation_rule: str | None = None
    table_rule: str | None = None
    source_universe: str | None = None
    comparator_evidence: str | None = None
    zero_failure_status_convention: str | None = None
    execution_or_host_policy: str | None = None
    artifact_provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class RelationMaterializationReport:
    """Outcome-free materialization report for one relation-specific card."""

    relation_type: RelationType
    status: MaterializationStatus
    missing_fields: tuple[str, ...] = ()
    required_fields: tuple[str, ...] = ()
    evidence_boundary: str = ""
    artifact_provenance: tuple[str, ...] = ()

    @property
    def feasible(self) -> bool:
        return self.status is MaterializationStatus.MATERIALIZED


@dataclass(frozen=True)
class RelationAuditResult:
    """Common return shape for relation-specific checkers."""

    verdict: str
    relation_type: RelationType
    evidence_boundary: str
    materialization_status: MaterializationStatus
    provenance_files: tuple[str, ...] = ()
    sensitivity_summary: str | None = None
    statistics: Mapping[str, Any] = field(default_factory=dict)


class RelationChecker(Protocol):
    """Interface implemented by relation-specific audit checkers."""

    def check(self, card: Any, artifact_inputs: Mapping[str, Any]) -> RelationAuditResult:
        """Return a relation-specific result for a materialized card."""


GENERIC_RELATION_FIELDS: tuple[str, ...] = (
    "relation_type",
    "metric",
    "source_universe",
    "comparator_evidence",
    "relation_rule",
    "zero_failure_status_convention",
    "artifact_provenance",
)

SCALAR_DIRECTIONAL_FIELDS: tuple[str, ...] = (
    "baselines",
    "metric",
    "direction",
    "instance_universe",
    "active_axes",
    "comparator_implementation",
    "metric_computation",
    "resource_budget",
)

HOST_POLICY_RELATIONS = {RelationType.RUNTIME_RATIO}


def _coerce_relation_type(value: RelationType | str) -> RelationType:
    if isinstance(value, RelationType):
        return value
    return RelationType(str(value))


def _get(obj: Any, field_name: str) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(field_name)
    return getattr(obj, field_name, None)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def infer_relation_type(card: Any) -> RelationType:
    """Infer a relation type from a card-like object or mapping."""

    relation = _get(card, "relation")
    if isinstance(relation, RelationSpec):
        return relation.relation_type
    raw = _get(card, "relation_type")
    if raw:
        return _coerce_relation_type(raw)
    return RelationType.SCALAR_DIRECTIONAL


def check_relation_materialization(
    card: Any,
    *,
    relation_type: RelationType | str | None = None,
) -> RelationMaterializationReport:
    """Check whether a card exposes the fields needed by its relation type.

    This is deliberately outcome-free. It validates field availability only; it
    does not compute margins, aggregate values, Wilson intervals, or verdicts.
    """

    rtype = _coerce_relation_type(relation_type) if relation_type else infer_relation_type(card)
    if rtype is RelationType.SCALAR_DIRECTIONAL:
        required = SCALAR_DIRECTIONAL_FIELDS
    else:
        required = GENERIC_RELATION_FIELDS
        if rtype in HOST_POLICY_RELATIONS:
            required = (*required, "execution_or_host_policy")

    missing = tuple(field for field in required if not _present(_get(card, field)))
    status = MaterializationStatus.MATERIALIZED if not missing else MaterializationStatus.INFEASIBLE
    boundary = "" if not missing else "missing relation materialization fields: " + ", ".join(missing)
    provenance = _get(card, "artifact_provenance")
    if isinstance(provenance, str):
        provenance_files = (provenance,)
    else:
        provenance_files = tuple(provenance or ())
    return RelationMaterializationReport(
        relation_type=rtype,
        status=status,
        missing_fields=missing,
        required_fields=tuple(required),
        evidence_boundary=boundary,
        artifact_provenance=provenance_files,
    )
