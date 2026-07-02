from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DRR:
    drr_id: str
    cro_id: str
    factors: dict[str, list[object]]  # {factor_name: [values]}
    admissibility: dict[str, str]  # {factor_name: admissible / borderline / non-admissible}
    preset_name: str  # compilation-only / sampling-only / combined-light
