"""Audit-cell data structures.

An audit cell combines operational-scope choices with execution-environment
choices. The fields are intentionally lightweight so external adapters can
store richer metadata without changing the public concept.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AuditCell:
    """One point in S_audit = S_scope x E_env."""

    cell_id: str
    scope: Mapping[str, Any] = field(default_factory=dict)
    l1_compilation: Mapping[str, Any] = field(default_factory=dict)
    l2_execution: Mapping[str, Any] = field(default_factory=dict)
    l3_backend: Mapping[str, Any] = field(default_factory=dict)
    algorithmic: Mapping[str, Any] = field(default_factory=dict)

    def metadata(self) -> dict[str, Mapping[str, Any] | str]:
        return {
            "cell_id": self.cell_id,
            "scope": self.scope,
            "l1_compilation": self.l1_compilation,
            "l2_execution": self.l2_execution,
            "l3_backend": self.l3_backend,
            "algorithmic": self.algorithmic,
        }
