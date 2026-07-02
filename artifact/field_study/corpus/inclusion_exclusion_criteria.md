# Corpus Construction, Inclusion, and Exclusion Criteria

This file documents how the RQ1 paper corpus was built and screened. It covers
(1) the construction/search protocol, (2) the screened-pool schema, (3) the
inclusion rule, (4) the exclusion taxonomy with realized counts, and (5) the
paper-level funnel. The retrieval log, candidate records, screened pool, and
inclusion/exclusion decisions are all archived (Sections 1, 2, and 6); counts that
are not derivable from a materialized file are not fabricated.

## 1. Construction / search protocol

The corpus was constructed through a **Google Scholar search-and-screen protocol**.
The artifact preserves the fixed screened-paper list and the normalized provenance
needed to inspect RQ1. Because the reviewer package uses canonical identifiers for
screened papers, many rows are keyed by `arxiv_id` where available; this is a canonical
identifier, not a claim that every result came directly from an arXiv API search. See
`search_protocol.md` in this directory.

- **Scope (paradigms).** Two scoped paradigms: compilation/transpilation and
  variational optimization (VQE/QAOA-family). Papers outside both are excluded as
  `out_of_scope_paradigm`.
- **Retrieval log.** The candidate pool was seeded by **13 predefined query strings**
  combining quantum-software terms with comparison terms. The full query log is archived
  in `search_log.csv` (in this directory; normalized query string, result count, export
  timestamp, status); the `all:"..."` notation there is a normalized archived query
  representation, not an arXiv API-only provenance claim. The de-duplicated, screened
  pool — each paper with its screening decision and exclusion reason — is published in
  `paper_list_250_screened.csv` in this directory. The 13 queries and their
  result counts were:

  | # | query (normalized `all:` representation) | result count |
  |---:|---|---:|
  | 1 | `"quantum compiler" AND "benchmark"` | 51 |
  | 2 | `"quantum compiler" AND "comparison"` | 11 |
  | 3 | `"quantum compilation" AND "benchmark"` | 51 |
  | 4 | `"quantum compilation" AND "comparison"` | 10 |
  | 5 | `"transpiler" AND "benchmark"` | 43 |
  | 6 | `"transpiler" AND "comparison"` | 9 |
  | 7 | `"QAOA" AND "benchmark"` | 163 |
  | 8 | `"QAOA" AND "comparison"` | 51 |
  | 9 | `"VQE" AND "ansatz comparison"` | 0 |
  | 10 | `"variational quantum" AND "benchmark"` | 200 |
  | 11 | `"variational quantum" AND "comparison"` | 119 |
  | 12 | `"quantum software" AND "benchmark"` | 38 |
  | 13 | `"quantum software" AND "comparison"` | 9 |

  Raw hits overlap heavily across queries; the de-duplicated, review-screened pool
  is 250 papers (see the contribution table below and Sections 4-5).
- **Search and export dates.** The corpus search was initially run on **2026-01-28**.
  `search_log.csv` carries the archived retrieval/export timestamp `2026-04-28T19:33:02`
  (a single batch timestamp); no per-query or per-paper retrieval dates are stored, and
  none are inferred here. The screened 250-paper corpus is fixed in
  `paper_list_250_screened.csv`.
- **Realized publication window.** The `published_date` column of the 250 retained
  candidates spans **2020-02-23 → 2024-12-23**. This is the realized publication
  window of the pool; no separately specified intended-query window is stored.
- **Candidate pool after de-duplication and review.** Each retained paper is
  attributed to one source query; after de-duplication, the 250-paper pool
  decomposes by contributing query as:

  | unique papers in pool | source query |
  |---:|---|
  | 90 | `"QAOA" AND "benchmark"` |
  | 62 | `"variational quantum" AND "comparison"` |
  | 27 | `"QAOA" AND "comparison"` |
  | 26 | `"quantum compiler" AND "benchmark"` |
  | 19 | `"transpiler" AND "benchmark"` |
  | 16 | `"quantum software" AND "benchmark"` |
  | 5 | `"transpiler" AND "comparison"` |
  | 3 | `"quantum software" AND "comparison"` |
  | 2 | `"quantum compiler" AND "comparison"` |
  | **250** | **total** |

  The four queries absent from this table contributed no additional unique papers
  after de-duplication (their hits were already retrieved by an earlier query, or
  returned zero results). Screening this 250-paper pool yields 119 include / 131
  exclude (Sections 4-5).
- **What the search does *not* produce.** The retrieval and screening pipeline
  produces *papers*, not audit-ready claims. The planning-ready claim count is a
  downstream product of claim extraction and the operationalizability/specification
  screen, not a search-query output:

  ```
  250 screened papers → 119 included papers → 457 verbatim-verified comparative claims
                       (455 accepted after source-grounded Layer-1 adjudication)
  ```

  Note on 457 vs 455: 457 is the raw verbatim-verified extraction count
  (`claims/extracted_claims_457.csv`); the source-grounded Layer-1 adjudication then
  demotes two non-comparator claims, giving the **455 accepted** comparative claims
  used throughout the paper and funnel (paradigm split 142 compilation / 313
  variational). The authoritative count map is `../../corrected_headline_counts.csv`
  and `../RELATION_SCHEMA_RQ1_COUNTS.md` (`accepted comparative claims | 455 | 457`).
  The downstream planning/auditable counts (175 claim cards, 79 scalar-directional
  planning records, 53 auditable designs, 8 exact) are products of the
  specification screen and materialization test applied after extraction, not search
  outputs.

## 2. Screened-pool schema

`paper_list_250_screened.csv` is the full screened pool (250 rows). Columns:

| column | meaning |
|---|---|
| `arxiv_id` | canonical identifier for the screened paper where available (version-pinned) |
| `title` | paper title |
| `published_date` | screened-paper publication date (canonical metadata; range is a paper-metadata range, not a search-source range) |
| `authors` | redacted for anonymous review |
| `screening_decision` | `include` or `exclude` |
| `exclusion_reason` | exclusion-taxonomy label (empty when included) |
| `screening_confidence` | `HIGH` / `MEDIUM` / `LOW` |
| `screening_notes` | free-text rationale for the decision |

The 119 `include` rows of `paper_list_250_screened.csv` are the RQ1 corpus.

`paper_list_250_screened.csv` carries the screened pool: 250 screened papers keyed by
canonical identifier (arXiv ID where available) with the 119 include / 131 exclude
split, the screening decision, and the exclusion reason. Per-query normalized
provenance is in `search_log.csv`.

## 3. Inclusion rule

Include a paper only if **all** of the following hold:

1. It is within compilation/transpilation **or** variational-optimization scope.
2. It contains at least one comparative claim of the form *A op B on metric M*
   (one named object compared against another on a quantitative metric).
3. The comparison is grounded in a **quantitative** metric (resource count,
   runtime, fidelity, approximation ratio, depth, probability, etc.).

Papers that are quantum-software-adjacent but do not satisfy all three are
excluded with the most specific applicable taxonomy label.

## 4. Exclusion taxonomy (with realized counts)

Standard exclusion labels and the count realized in `paper_list_250_screened.csv`
(131 excluded of 250 screened):

| exclusion_reason | count | meaning |
|---|---:|---|
| `out_of_scope_paradigm` | 66 | quantum-software-adjacent but outside the two scoped paradigms |
| `application_paper` | 31 | uses quantum methods for an application; no in-scope tool/method comparison |
| `hardware_only` | 15 | device/hardware-centric; not a software-stack comparison |
| `no_quantitative_claim` | 9 | no quantitative comparative metric |
| `algorithm_complexity_only` | 3 | purely theoretical/complexity, no empirical comparative benchmark |
| `pulse_level_only` | 3 | pulse-level / direct-control optimization, out of scope |
| `error_correction_only` | 2 | error-correction / fault-tolerance centric |
| `survey_paper` | 2 | survey/review, not a primary comparative study |
| **total excluded** | **131** | |

## 5. Paper-level funnel

```
250 screened candidates
 └─ 131 excluded (taxonomy above)
 └─ 119 included  → RQ1 corpus (119 include rows of paper_list_250_screened.csv)
```

The 119 included papers are the input to claim extraction (Stage 1); the
claim-level funnel (630 → 628 → 457 raw extraction records) is summarized below; the
accepted count after Layer-1 adjudication is 455 (`../../corrected_headline_counts.csv`).

## 6. Provenance notes

- The retrieval log (`search_log.csv`, in this directory) and the curated screened
  pool with per-row screening decisions and exclusion reasons
  (`paper_list_250_screened.csv`) **are** archived and reproducible from the artifact.
- The 13 query strings and their raw hit counts, the single retrieval batch
  timestamp (`2026-04-28T19:33:02`), and the realized publication window
  (2020-02-23 → 2024-12-23) are recorded in Section 1 and in `search_log.csv`.
- No per-query or per-paper retrieval *dates* beyond that single batch timestamp are
  stored, and none are inferred. There is no separate intended-query-window record
  beyond the realized publication span. The complete row-level claim-deduplication
  worksheet (Stage 2 → Stage 3) is not part of the archive.
