# Corpus search protocol

This file records how to inspect the corpus-search provenance used for RQ1.

The manuscript describes the discovery step as a **Google Scholar search-and-screen
protocol**. The search was initially run on 2026-01-28 using 13 predefined query
strings combining quantum-software terms with comparison terms. The artifact records
the archived retrieval/export timestamp as `2026-04-28T19:33:02`.

The artifact does not rely on raw Google Scholar pages for reviewer checks, and raw
Google Scholar result pages/snapshots are not bundled. Instead, it preserves normalized
reviewer-facing provenance: query terms and counts in
[search_log.csv](search_log.csv), the fixed 250-paper screened list in
[paper_list_250_screened.csv](paper_list_250_screened.csv), screening decisions and
exclusion reasons, raw extraction records, corrected adjudication/count files, and
coding-validity evidence.

In [search_log.csv](search_log.csv), the `all:"..."` notation is a normalized archived
query representation. It should not be read as a claim that the submitted corpus was
built from an arXiv API-only search. In
[paper_list_250_screened.csv](paper_list_250_screened.csv), `arxiv_id` is used as a
canonical identifier for screened papers where available.

The fixed RQ1 evidence chain is:

- 250 screened papers in [paper_list_250_screened.csv](paper_list_250_screened.csv);
- 119 included papers via `screening_decision=include`;
- 457 raw Stage-3 extraction records in [../claims/extracted_claims_457.csv](../claims/extracted_claims_457.csv);
- 455 final accepted claims after correction in [../../corrected_headline_counts.csv](../../corrected_headline_counts.csv) and [../../source_grounded_claim_adjudication.csv](../../source_grounded_claim_adjudication.csv);
- the six-row Table III disposition summary in [../rq1_materialization_barrier_taxonomy.csv](../rq1_materialization_barrier_taxonomy.csv), with all 79 supporting records in `../rq1_materialization_barrier_records_79.csv`.

See also [inclusion_exclusion_criteria.md](inclusion_exclusion_criteria.md) for the
screening protocol, exclusion taxonomy, and paper-level funnel.
