from __future__ import annotations


def remap_status(
    raw_stability: str,
    anchor_support: bool,
    has_stable_reverse: bool,
    has_subregion_candidate: bool,
    subregion_valid: bool,
) -> str:
    if has_stable_reverse:
        return "Reversed"
    if raw_stability == "stable" and anchor_support:
        return "Sustained"
    if raw_stability in ["unstable", "inconclusive"]:
        if anchor_support and has_subregion_candidate and subregion_valid:
            return "Scope-limited"
        return "Unresolved"
    if raw_stability == "stable" and not anchor_support:
        return "Reversed"
    return "Unresolved"
