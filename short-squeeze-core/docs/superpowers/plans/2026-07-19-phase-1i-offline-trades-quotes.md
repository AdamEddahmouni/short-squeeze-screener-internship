# Phase 1I Offline Trade and Quote Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add offline deterministic trade/quote normalization, immutable point-in-time microstructure evidence, sequence-aware objective series, replay fixtures, and local CLI support without analytics or trading interpretation.

**Architecture:** Reuse schema `1.0.0`, canonical `TRADE`/`QUOTE` observations, the shared adapter result/diagnostic boundary, replay engine, and evidence bundle. Make only two compatibility-tested contract relaxations, retain detailed provider semantics in structured provenance, add independent `TRADES`/`QUOTES` coverage, and build one pure structural series over eligible observations.

**Tech Stack:** Python 3.12, Pydantic 2.13.4, pytest 8.4.1, and standard-library decimal/datetime/hash/UUID/JSON/path/CLI APIs.

## Global Constraints

- Work only on `phase/1i-offline-trades-quotes`; do not merge, push, add a remote, or amend old commits.
- Keep schema `1.0.0`; preserve all Phase 1A-1H observation, replay, bundle, and serialization anchors.
- Use only `SANITIZED_REPRESENTATIVE_SAMPLE` and `SYNTHETIC_EDGE_CASE`; no recorded row was found.
- Use red-green-refactor for every production behavior and make focused commits.
- Add no network/provider client, credentials, environment reads, database, GUI, order path, wall clock, random identity, analytics dependency, depth book, synthetic NBBO, bar aggregation, aggressor side, buy/sell volume, order flow, midpoint, spread, slippage, liquidity, momentum, score, rank, recommendation, or signal.

---

### Task 1: Canonical compatibility relaxations

**Files:**
- Modify: `src/squeeze_core/contracts/payloads.py`
- Modify: `src/squeeze_core/contracts/observation.py`
- Test: `tests/test_trade_quote_contract.py`

**Interfaces:**
- Produces: `TradePayload(price: Decimal, size: int | None, exchange: str | None, conditions: tuple[str, ...])` and objective crossed `QuotePayload` acceptance.

- [ ] Write tests asserting missing trade size validates, zero differs from missing, negative/fractional size rejects, crossed quote accepts known quality, and committed Phase 1A-1H anchors remain unchanged.
- [ ] Run `\.\.venv\Scripts\python.exe -m pytest tests\test_trade_quote_contract.py -q`; expect failures for missing size and known-quality crossed quote.
- [ ] Change only the trade-size annotation/default and remove only the crossed-quality validator branch.
- [ ] Re-run focused contract/serialization tests; expect pass with identical legacy canonical JSON.
- [ ] Commit `feat: relax canonical trade quote compatibility`.

### Task 2: Strict offline provider record, enums, and parsing

**Files:**
- Create: `src/squeeze_core/adapters/trades_quotes/{__init__,models,parsing,conditions,sequencing,semantics,validation}.py`
- Modify: `src/squeeze_core/adapters/diagnostics.py`
- Test: `tests/adapters/trades_quotes/test_models_and_parsing.py`

**Interfaces:**
- Produces: `TradeQuoteRecord`, `TradeQuoteRecordType`, `TradeQuoteLifecycleStatus`, `SequenceScope`, `MarketScope`, `SizeUnit`, `QuoteMarketState`, `UnknownAvailabilityPolicy`, `parse_trade_quote_timestamp`, and `quote_market_state`.

- [ ] Write failing tests for strict schema/type/origin, symbol/asset class, provider/venue, record identity, exact timestamps, availability policies, prices/sizes, conditions, one/two-sided quotes, scope, sequence scope, lifecycle fields, and alias rejection.
- [ ] Run the focused test; expect import failure because the package is absent.
- [ ] Implement immutable models and pure parsing/validation with stable typed diagnostic errors.
- [ ] Re-run the focused test; expect all cases pass.
- [ ] Commit `feat: add offline trade and quote provider contracts`.

### Task 3: Deterministic trade normalization

**Files:**
- Create: `src/squeeze_core/adapters/trades_quotes/normalizer.py`
- Modify: `src/squeeze_core/adapters/trades_quotes/__init__.py`
- Test: `tests/adapters/trades_quotes/test_trade_normalizer.py`

**Interfaces:**
- Produces: `normalize_trade_quote_record(record, context) -> NormalizationResult` and `normalize_trade_quote_records(records, context) -> NormalizationResult`.

- [ ] Write failing tests for complete trade; missing/zero/negative/invalid price; missing/zero/negative/fractional size; units; known/unknown/multiple conditions; venue; publication/receipt/effective gates; unknown availability policies; original/corrected/cancelled records; duplicate; same-ID conflict; cross-provider independence; and repeat hashes.
- [ ] Run the focused test and confirm failure because normalization is absent.
- [ ] Implement minimal trade mapping into canonical observations with exact Decimal, nullable size, provenance metadata, quality, lifecycle links, and deterministic batch duplicate/conflict handling.
- [ ] Re-run focused trade plus legacy contract/replay tests; expect pass.
- [ ] Commit `feat: add deterministic trade normalization`.

### Task 4: Deterministic quote normalization

**Files:**
- Modify: `src/squeeze_core/adapters/trades_quotes/normalizer.py`
- Test: `tests/adapters/trades_quotes/test_quote_normalizer.py`

**Interfaces:**
- Extends the Task 3 functions for canonical `QUOTE` observations.

- [ ] Write failing tests for two-sided/bid-only/ask-only; missing both; missing/zero/negative/fractional size; invalid price; venue/NBBO/consolidated/aggregated/unknown scope; condition/source; normal/locked/crossed/unknown state; availability; lifecycle; duplicates/conflicts; cross-provider independence; and unknown venue.
- [ ] Run the focused test and confirm expected failures for absent quote mapping.
- [ ] Implement quote mapping without fabricating sides, merging venues, or calculating midpoint/spread.
- [ ] Re-run focused adapter and compatibility tests; expect pass.
- [ ] Commit `feat: add deterministic quote normalization`.

### Task 5: Point-in-time domains, ages, relationships, and conflicts

**Files:**
- Modify: `src/squeeze_core/evidence/{models,policy,builder,conflicts,__init__}.py`
- Test: `tests/evidence/test_trade_quote_timeline.py`
- Test: `tests/evidence/test_trade_quote_conflicts.py`

**Interfaces:**
- Produces: `CoverageDomain.TRADES`, `CoverageDomain.QUOTES`, `include_trades_domain`, `include_quotes_domain`, trade/quote evidence diagnostics, five separate ages, revision relationships, and compatible conflicts.

- [ ] Write failing timeline tests for before publication, publication-before-receipt, original receipt, correction/cancellation receipt, future event, unknown availability, independent missing/partial/conflicted coverage, and historical byte stability.
- [ ] Write failing conflict tests for same identity, compatible sequence/event conflicts, incompatible scope/venue/unit separation, lifecycle exclusions, cross-provider preservation, and no winner/average.
- [ ] Run focused tests and confirm missing domains/gates.
- [ ] Implement conditional bundle fields/defaults so inactive Phase 1A-1H bundles serialize unchanged.
- [ ] Re-run focused evidence plus every prior replay integration test; expect pass.
- [ ] Commit `feat: enforce point-in-time trade and quote evidence`.

### Task 6: Sequence-aware objective series

**Files:**
- Create: `src/squeeze_core/evidence/trades_quotes.py`
- Modify: `src/squeeze_core/evidence/__init__.py`
- Test: `tests/evidence/test_trade_quote_series.py`

**Interfaces:**
- Produces: `TradeQuoteSeriesPolicy`, `TradeQuoteSeriesDiagnosticCode`, `TradeQuoteSeries`, and `build_trade_quote_series(observations, policy)`.

- [ ] Write failing tests for symbol/provider/venue/scope filters; event ordering; comparable sequence ordering; arrival metadata; ordered/out-of-order/duplicate/reset/missing sequence; incompatible scopes; latest IDs; lifecycle versions; normal/locked/crossed/one-sided quote states; publication/receipt/future-event exclusions; and repeatable hash.
- [ ] Run the focused test and confirm wished-for API import failure.
- [ ] Implement pure selection/structural diagnostics with no cross-scope comparison or analytical fields.
- [ ] Re-run focused series tests; expect pass and byte-identical repeated output.
- [ ] Commit `feat: add sequence-aware trade and quote evidence`.

### Task 7: Provider, lifecycle, sequence, and mixed replay fixtures

**Files:**
- Create: `tests/fixtures/providers/trades_quotes/{fixture_metadata,context,trade_representative_cases,trade_edge_cases,trade_lifecycle_cases,quote_representative_cases,quote_edge_cases,quote_lifecycle_cases}.json`
- Create: `tests/fixtures/evidence/{mixed_phase_1i_cases,trade_quote_availability_timeline,expected_phase_1i_bundle_metadata}.json`
- Create: `tests/fixtures/evidence/normalized_phase_1i_point_in_time.jsonl`
- Create: `tests/phase_1i_fixture_builders.py`
- Test: `tests/adapters/trades_quotes/test_provider_fixtures.py`
- Test: `tests/evidence/test_phase_1i_replay_integration.py`

**Interfaces:**
- Produces deterministic fixture families, lifecycle checkpoints, sequence cases, mixed JSONL, bundles, series, raw/observation/replay/hash anchors, and embedded Phase 1A-1H anchors.

- [ ] Write failing integrity/replay tests enumerating every required trade/quote case, exact provenance labels/metadata, no credentials/accounts/real symbols/live URLs, all prior domains, independent new coverage, lifecycle checkpoints, strategy-neutral key scan, and repeated artifact equality.
- [ ] Run focused tests and confirm missing fixtures/builders.
- [ ] Add representative/synthetic JSON and a deterministic generator using only pure local normalizers/builders.
- [ ] Generate twice; assert byte-identical files, observations, replay, timelines, series, bundle serialization, and all prior anchors.
- [ ] Commit `test: add trade quote lifecycle and mixed replay fixtures`.

### Task 8: Offline CLI

**Files:**
- Modify: `src/squeeze_core/__main__.py`
- Test: `tests/test_trade_quote_cli.py`

**Interfaces:**
- Extends `normalize-provider --provider trades-quotes`.
- Produces `build-trade-quote-series --input PATH --symbol SYMBOL --as-of TIMESTAMP` with optional provider/venue/scope filters.

- [ ] Write failing CLI tests for accepted trade/quote, rejected/nonzero record, deterministic JSON, timeline command reuse, objective series filters, and forbidden analytical/trading keys.
- [ ] Run focused CLI tests and confirm parser/provider failures.
- [ ] Register the new local provider and series command using existing JSON/error conventions.
- [ ] Re-run CLI and full tests; expect pass.
- [ ] Commit `feat: extend offline cli for trade and quote evidence`.

### Task 9: ADRs and user documentation

**Files:**
- Create: `docs/adr/0026-trade-quote-availability.md`
- Create: `docs/adr/0027-sequence-scope-and-out-of-order-evidence.md`
- Create: `docs/adr/0028-crossed-and-locked-quotes-without-signals.md`
- Create: `docs/providers/trades-quotes-offline.md`
- Create: `docs/trade-quote-availability-semantics.md`
- Create: `docs/trade-quote-sequence-and-lifecycle-timeline.md`
- Create: `docs/phase-1i-progress.md`
- Modify: `README.md`, `docs/{architecture,adapter-contract,observation-contract,field-semantics,cross-source-evidence,point-in-time-evidence-policy,testing-and-validation}.md`
- Test: `tests/test_phase_1i_documentation.py`

**Interfaces:**
- Documents every availability, venue/scope, sequence, lifecycle, fixture provenance, compatibility, objective-state, and strict-exclusion decision.

- [ ] Write a failing documentation test for required files/phrases and forbidden claims.
- [ ] Run it and confirm missing documentation.
- [ ] Add concise docs and ADRs consistent with implemented interfaces and hashes.
- [ ] Re-run documentation and full tests; expect pass.
- [ ] Commit `docs: document point-in-time trade and quote evidence`.

### Task 10: Final deterministic and isolation verification

**Files:**
- Modify only if a failing verification first proves a Phase 1I defect.

**Interfaces:**
- Produces the completion evidence, not a new runtime interface.

- [ ] Run the focused adapter, evidence, fixture, CLI, contract, serialization, and documentation suites.
- [ ] Run `\.\.venv\Scripts\python.exe -m pytest`; require zero failures and only the unchanged timezone-data skip.
- [ ] Run fixture generation twice and record raw/observation/mixed JSONL/replay/timeline/series/final bundle hashes.
- [ ] Run CLI normalization, timeline, and series smoke commands twice and compare bytes.
- [ ] Search source/fixtures for credentials, network/auth/database/GUI/order/wall-clock/random/analytics/strategy patterns and inspect every match.
- [ ] Verify the three archived repositories remain clean at required commits, Phase 1A-1H anchor files match, implementation branch is correct, remotes are empty, and working tree is clean after a final verification commit if needed.

