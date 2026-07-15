from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExternalClaimRecord:
    external_claim_id: str
    source_id: str
    source_title: str
    source_type: str
    venue_year: int
    source_url: str
    artifact_url: str
    claim_type: str
    paper_claim_text: str
    claim_text_formalized: str
    evidence_origin: str
    compared_objects: list[str]
    primary_metric: str
    task_family: str
    benchmark_family: str
    anchor_setting: str
    claim_scope_as_stated: str
    baseline_justification: str
    admissible_variation_candidates: list[str] = field(default_factory=list)
    excluded_variation_candidates: list[str] = field(default_factory=list)
    suite_category: str = "transpiler_compiler"
    artifact_backed: bool = False
    rerunnable: str = "no"
    auditability_tier: str = "formalizable_not_rerunnable"
    paper_claim_vs_artifact_gap: str = ""
    ingestion_status: str = "raw"
    execution_adapter: str = "local_csv_binary_outcomes"
    local_input_relpath: str | None = None
    local_execution_notes: str = ""
    notes_caveats: str = ""
    anchor_evidence_ref: str | None = None
    drr_seed_notes: str | None = None
    oap_seed_notes: str | None = None
    claim_family: str = "comparative"
    claim_text: str | None = None
    claim_text_original: str | None = None
    metric: str | None = None

    def __post_init__(self) -> None:
        if self.claim_text_original is None:
            self.claim_text_original = self.paper_claim_text
        if self.metric is None:
            self.metric = self.primary_metric
        if self.claim_text is None:
            if self.claim_text_formalized:
                self.claim_text = self.claim_text_formalized
            else:
                self.claim_text = self.paper_claim_text
