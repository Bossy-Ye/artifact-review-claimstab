from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OAP:
    oap_id: str
    cro_id: str
    drr_id: str
    anchor_config_id: str
    selection_policy: str  # full_factorial / adaptive_ci / random_k
    audit_intent: str  # e.g. validate_comparative_claim
    traceability: dict[str, object]  # run bundle refs / artifact ids
