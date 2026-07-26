# Phase 1F Progress

Phase 1F is implemented on `phase/1f-offline-trading-halts` as a local-only, deterministic trading-halt evidence slice.

## Delivered

- strict exchange-shaped halt input contract and conservative timestamp parsing
- deterministic single/batch normalization with raw-input hashes
- immutable duplicate, conflict, and revision handling
- scheduled versus actual quote/trade resumption semantics
- strict publication, receipt, and effective-time eligibility
- independent `TRADING_HALTS` coverage and objective halt-state summaries
- halt conflicts, revision relationships, ages, replay, timeline, and CLI support
- 30 representative/synthetic provider cases, 15 mixed evidence scenarios, a 12-observation mixed JSONL, and deterministic fixture generation
- ADRs 0017–0019 covering availability, scheduled/actual separation, and immutable lifecycle updates

The canonical schema remains `1.0.0`; the existing `TradingHaltPayload` was sufficient. Lifecycle detail is additive provider metadata, preserving all earlier canonical compatibility anchors.

## Deterministic anchors

- mixed JSONL: `c5cb4b76f75b73ba89165edcf53d60a39cee193c103b718f163991a02a4106c4`
- strict replay: `1c1a9e84de1dfdbff032642ba6616e2573cb25e5965eb059b031ca136006f937`
- final bundle: `af9c72db36d3b3bccba590c6580e74a5922bad7f2d826107ca9f529c66b48ae5`
- serialized final bundle: `79aea01b32b873e39e5c27860bf5821fbe198259a53a8623df83e99cb9786f27`

The full suite contains 346 tests. Final verification also regenerates artifacts twice, exercises all Phase 1F CLI paths, checks forbidden runtime boundaries, and confirms the archived repositories remain unchanged.

## Explicit exclusions

There is no live exchange integration, download, socket/stream, credentials, account access, order path, persistence service, news interpretation, sentiment, scoring, ranking, prediction, or recommendation. Fixture provenance is representative/synthetic because archive search found no preserved recorded trading-halt row.
