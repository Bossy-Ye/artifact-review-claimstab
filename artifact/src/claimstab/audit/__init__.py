"""Paper-facing audit primitives for ClaimStab-QC."""

from .cells import AuditCell
from .claims import ComparativeClaim, MetricDirection, direction_preserved, signed_margin
from .relation_checkers import ScalarDirectionalWilsonChecker, get_relation_checker
from .relations import (
    BoundaryVerdict,
    MaterializationStatus,
    RelationAuditResult,
    RelationMaterializationReport,
    RelationSpec,
    RelationType,
    check_relation_materialization,
    infer_relation_type,
)
from .runner import preservation_outcomes, signed_margins
from .verdicts import ClaimStatus, classify_direction_preservation

__all__ = [
    "AuditCell",
    "ClaimStatus",
    "ComparativeClaim",
    "MetricDirection",
    "BoundaryVerdict",
    "MaterializationStatus",
    "RelationAuditResult",
    "RelationMaterializationReport",
    "RelationSpec",
    "RelationType",
    "ScalarDirectionalWilsonChecker",
    "classify_direction_preservation",
    "check_relation_materialization",
    "direction_preserved",
    "get_relation_checker",
    "infer_relation_type",
    "preservation_outcomes",
    "signed_margin",
    "signed_margins",
]
