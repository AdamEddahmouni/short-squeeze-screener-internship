# Phase 1H Progress

Phase 1H is implemented on `phase/1h-offline-market-bars` as local-only deterministic market-bar normalization and objective evidence.

## Delivered

- strict provider-neutral model and documented IBKR-, Schwab-, Yahoo-, and generic-shaped aliases
- unchanged schema `1.0.0` and unchanged canonical `BarPayload`
- explicit fixed/daily interval, start-inclusive/end-exclusive boundary, timezone, DST, session, volume-unit, and missing-versus-zero semantics
- immutable partial/completed/corrected/cancelled lifecycle with duplicate, conflict, overlap, revision, publication, receipt, and effective-time handling
- independent `MARKET_BARS` coverage, interval/correction ages, and deterministic session-aware objective series
- 43 representative/synthetic provider cases, including complete 15-minute and 1-hour bars plus explicit zero trade count; 18-observation mixed replay; six availability bundles; local CLI commands; and ADRs 0023-0025

## Deterministic anchors

Canonical values are stored in `tests/fixtures/evidence/expected_phase_1h_bundle_metadata.json`. Phase 1G anchors remain byte-for-byte unchanged.

## Explicit exclusions

There is no live or streaming adapter, network client, credential access, downloader, provider SDK, database, exchange calendar, indicator, relative-volume or momentum computation, strategy formula, score, rank, signal, prediction, recommendation, order path, persistence service, web API, or GUI.
