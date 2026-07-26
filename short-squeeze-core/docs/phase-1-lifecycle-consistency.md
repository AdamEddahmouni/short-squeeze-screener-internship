# Phase 1 Lifecycle Consistency Matrix

This matrix records how each lifecycle-bearing domain preserves immutability, links revisions,
and keeps historical bundles stable. The uniform guarantees are proven cross-domain by
`tests/compatibility/test_phase_1_lifecycle.py` and per-domain by the existing
`tests/evidence/test_*_timeline.py` suites.

## Uniform lifecycle guarantees

- **Immutability** — observations are frozen pydantic models; a later record never mutates an
  earlier one.
- **No look-ahead** — a correction, cancellation, withdrawal, or deletion that becomes available
  after `as_of` is invisible to an earlier bundle. Eligibility is monotonic as `as_of` advances.
- **Historical stability** — rebuilding a bundle at a fixed `as_of` is byte-identical across runs
  (`bundle_hash` and `canonical_hash` stable).
- **Preservation** — a correction never overwrites its prior; a cancellation never deletes its
  prior. Both the prior and successor remain present, linked by an explicit relationship.
- **Diagnosed gaps** — when an eligible revision references a prior that is not in the bundle, a
  `*_NOT_YET_AVAILABLE` INFO diagnostic is emitted instead of silently dropping the link.
- **Duplicate ≠ revision ≠ conflict** — exact duplicates, revision chains, and value conflicts are
  distinct classifications and never collapsed into one another.

## Per-domain lifecycle behavior

| Domain | Lifecycle statuses | Link mechanism | Relationship / state output | Proof (existing tests) |
| --- | --- | --- | --- | --- |
| PUBLISHED_SHORT_INTEREST | ORIGINAL → CORRECTED/REVISED/CANCELLED | `supersedes_source_record_id`, `parent_observation_ids` | `RevisionRelationship` + correction/supersedes diagnostics | `test_short_interest_timeline.py`, `test_short_interest_conflicts.py` |
| SEC_FILINGS | FILED → AMENDED (also CORRECTED/CANCELLED) | `amends_accession_number`, `parent_observation_ids` | `RevisionRelationship` + amendment diagnostics | `test_sec_filing_timeline.py`, `test_sec_filing_conflicts.py` |
| TRADING_HALTS | ANNOUNCED → … → RESUMED / CANCELLED / UPDATED / CORRECTED | `halt_event_key`, `supersedes_source_record_id` | `RevisionRelationship` + derived `HaltState` | `test_trading_halt_timeline.py`, `test_trading_halt_conflicts.py` |
| NEWS | ORIGINAL → UPDATED/CORRECTED/WITHDRAWN/DELETED (+ SYNDICATED) | `supersedes_provider_record_id`, `prior_canonical_url`, `parent_observation_ids` | `NewsRelationship` (REVISION/CORRECTION/WITHDRAWAL/DELETION/SYNDICATED) | `test_news_timeline.py`, `test_news_conflicts.py` |
| MARKET_BARS | PARTIAL → COMPLETED → CORRECTED → CANCELLED | `supersedes_provider_record_id`, provider+boundary chain | `RevisionRelationship` + bar lifecycle diagnostics | `test_market_bar_timeline.py`, `test_market_bar_conflicts.py`, `test_bar_series.py` |
| TRADES | ORIGINAL → CORRECTED/CANCELLED/DELETED | `supersedes_provider_record_id`, `parent_observation_ids` | `RevisionRelationship` + trade/quote diagnostics | `test_trade_quote_timeline.py`, `test_trade_quote_conflicts.py`, `test_trade_quote_series.py` |
| QUOTES | ORIGINAL → CORRECTED/CANCELLED/DELETED | `supersedes_provider_record_id`, `parent_observation_ids` | `RevisionRelationship` + trade/quote diagnostics | `test_trade_quote_timeline.py`, `test_trade_quote_conflicts.py` |

The snapshot and borrow domains (1B/1C) are point observations without a lifecycle revision
chain; cross-source disagreement is expressed as conflicts, not revisions.

## Cross-domain proof

`tests/compatibility/test_phase_1_lifecycle.py` loads the multi-domain Phase 1I fixture (all ten
domains, including immutable trade/quote original→corrected→cancelled chains) and asserts:

- eligibility is monotonic as `as_of` advances (no observation disappears);
- rebuilding at each `as_of` is byte-stable;
- corrections and cancellations keep their prior observations present;
- a cancellation never empties domain coverage.

Deterministic byte-stability of the historical Phase 1G/1H/1I bundles themselves is anchored in
`tests/compatibility/test_phase_1_anchor_manifest.py`.
