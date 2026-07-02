from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CRO:
    cro_id: str
    claim_type: str  # comparative / decision / distribution
    compared_objects: list[str]
    metric: str
    task_family: str
    claim_text: str  # original or reconstructed
    source: str  # internal / external
    anchor_config_id: str
    anchor_support: bool
