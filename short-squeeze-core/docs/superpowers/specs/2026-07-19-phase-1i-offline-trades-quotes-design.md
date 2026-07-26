# Phase 1I Offline Trade and Quote Evidence Design

## Scope and evidence basis

Phase 1I adds deterministic offline normalization and point-in-time reconstruction of objective trade and quote records. It answers which provider records were provider-available and locally received at a requested time, which provider/venue/scope/sequence/condition facts they carried, and whether their immutable structure was original, corrected, cancelled, duplicated, conflicted, one-sided, locked, crossed, missing-sequence, reset, or out of arrival order. It does not calculate aggressor side, buy/sell volume, imbalance, delta, midpoint, spread, slippage, impact, liquidity, momentum, scores, ranks, recommendations, or signals.

The three evidence repositories were verified clean at `0897562e05d75b812dd284de81dfafdfa1dea916`, `6dbefd1a6b271bfc48106c4aa002f211735551cd`, and `84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8`. Read-only searches found:

| Archived evidence | Shape | Limitation | Fixture disposition |
|---|---|---|---|
| `core/ib_api.py` | IB `reqMktData` request and ticker/current-price consumption | no saved tick, bid/ask, event timestamp, publication, venue, sequence, conditions, or lifecycle row | request-shape context only; unusable as a trade/quote fixture |
| `core/schwab_api.py` and `tests/test_schwab_api.py` | `lastPrice` quote/screener snapshot dictionaries | mocked/current snapshot semantics, not a transaction or bid/ask event | mocked snapshot evidence only; unusable as a trade/quote fixture |
| Phase 0 source map | IB market-data ticks and Schwab quotes existed in runtime | field-level source timestamps and entitlement were not retained | confirms the historical provenance gap, not a provider row |

No row has defensible provider origin plus field/timestamp/venue/sequence semantics. Phase 1I therefore uses only `SANITIZED_REPRESENTATIVE_SAMPLE` and `SYNTHETIC_EDGE_CASE`; no fixture is `SANITIZED_RECORDED_SAMPLE`. Provider-neutral `TRADE_QUOTE_V1` rows avoid inventing undocumented IBKR, Schwab, SIP, exchange, or proprietary-feed aliases.

## Canonical contract decision

Schema remains `1.0.0`. `TradePayload` and `QuotePayload` remain the canonical representations, with two minimal backward-compatible validation relaxations protected by compatibility tests:

1. `TradePayload.size` becomes `int | None`, defaulting to `None`, so an objectively reported trade price with unavailable size can preserve missing rather than fabricate zero or reject all usable evidence. Existing serialized trades with integer size are byte-identical.
2. The envelope no longer forces every crossed quote to `QualityState.INVALID`. Crossedness is a structural state, not proof of erroneous data. Existing crossed quotes carrying `INVALID` remain valid and byte-identical.

No field is added to either payload, so legacy serialization keys do not change. Trade price remains positive exact `Decimal`; quote prices remain nullable non-negative exact `Decimal`; sizes remain nullable non-negative integers. Trade conditions remain the existing canonical tuple. Quote condition/source, size unit, provider record identity, venue, sequence scope, market scope, lifecycle status, revision, publication, capture, and side identity stay in documented structured provenance. Envelope `sequence_number`, `exchange`, `source_record_id`, and parent/correlation relationships are reused.

## Offline record contract

`TradeQuoteRecord` is immutable and rejects unknown fields. It accepts only schema `TRADE_QUOTE_V1`, record type `TRADE` or `QUOTE`, fixture origin, provider and provider record identity, symbol, equity asset class, exchange/venue, optional sequence and explicit sequence scope, market session, event/publication/capture times, lifecycle status/revision/supersession, and sanitized metadata.

Trade rows contain exact positive price, nullable whole non-negative size, explicit size unit (`SHARES`, `CONTRACTS`, `UNITS`, `UNKNOWN`), and zero or more objective conditions. Quote rows contain independently nullable bid/ask price and size, side identities, quote condition/source, size unit, and market scope (`VENUE`, `NBBO`, `CONSOLIDATED`, `PROVIDER_AGGREGATED`, `UNKNOWN`). At least one quote side must contain price or size; missing both sides rejects. A size without its side price is preserved as structurally unusual and diagnosed, not converted into a price. Negative/fractional sizes reject. Zero remains zero and is diagnosed separately from missing.

Only equity rows are accepted in Phase 1I. Provider, exchange, and venue remain separate. Unknown venue/scope/conditions are valid explicit facts with diagnostics. A venue quote is never called NBBO unless the row explicitly says `NBBO`; no venue merge or synthetic NBBO exists.

## Time and availability

Event time describes when the provider says the transaction or quote occurred. Provider publication time describes provider availability. Capture time describes collection. Context ingestion is local receipt. Envelope fields map as follows:

- `source_timestamp`: defensible provider publication boundary;
- `received_timestamp`: context `ingested_at`;
- `effective_timestamp`: `max(publication_timestamp, received_timestamp)`;
- event and capture timestamps: structured provenance.

Event time never grants availability. `STRICT` rejects missing publication. `CAPTURE_AS_UNCERTAIN_PLACEHOLDER` and `RECEIPT_AS_UNCERTAIN_PLACEHOLDER` may establish an explicitly uncertain source boundary while retaining the original missing-publication fact and a stable diagnostic. Capture is never relabeled as publication. Point-in-time evidence and series require publication, receipt, and effective time no later than `as_of`; future event timestamps are excluded even when operational timestamps are earlier because they cannot objectively have occurred yet.

## Sequence, ordering, and structural quote state

Sequence scopes are `PROVIDER_GLOBAL`, `SYMBOL`, `VENUE`, `CHANNEL`, `SESSION`, and `UNKNOWN`. Missing and unknown scope remain explicit. Sequence comparison occurs only within a compatibility key containing provider, record type, declared scope, and the scope-specific symbol/venue/channel/session discriminator. Arrival order is input order, event order is event timestamp plus deterministic identity, and comparable sequence order is a separate view.

Within one compatible sequence stream, equal sequence/content is a duplicate, equal sequence/changed content is a conflict, lower sequence after a higher sequence is out of order unless an explicit reset marker starts a new generation, and a reset is diagnosed without comparing across generations. Incompatible scopes are never compared. Batch output order is canonical and independent of input order; input arrival indexes remain provenance.

Quote structural state is derived only when both side prices exist: `NORMAL` for bid below ask, `LOCKED` for equality, `CROSSED` for bid above ask, and `UNKNOWN` otherwise. These labels are objective structure only. No spread or midpoint value is calculated or serialized.

## Lifecycle, duplicates, and conflicts

Statuses are `ORIGINAL`, `CORRECTED`, `CANCELLED`, `DELETED`, and `UNKNOWN`. Every lifecycle row is a new immutable observation. Explicit supersession links produce parent observation IDs and deterministic correlation/revision relationships when the prior provider record is present. A missing prior link is diagnosed and the new row is retained. Cancellation/deletion preserves the provider-reported payload snapshot; it never removes the original from later bundles.

Exact raw duplicates emit once with a stable diagnostic. Same provider record ID or same compatible sequence identity with changed content is preserved as conflicted evidence. Direct comparison requires compatible symbol, asset class, provider/venue or market scope, event timestamp, sequence scope, size units, and lifecycle stage. Cross-provider reports remain independent and are never merged, averaged, or winner-selected.

## Evidence and deterministic series

`TRADES` and `QUOTES` are independent coverage domains with `PRESENT`, `MISSING`, `PARTIAL`, `STALE`, `DELAYED`, `UNKNOWN_FRESHNESS`, `CONFLICTED`, and `INVALID` states. Observation ages separately expose event, publication, availability, capture, and correction age. Existing bundle fields use excluded defaults so Phase 1A-1H serialized bundles remain byte-identical when the new domains are inactive.

`build_trade_quote_series` selects eligible records by symbol and optional provider/venue/market scope, returns distinct trade and quote tuples ordered by event time then only-compatible sequence metadata and deterministic identity, exposes latest eligible IDs and immutable lifecycle chains, and reports duplicate/out-of-order/reset/missing/incompatible sequence plus normal/locked/crossed/one-sided states. It does not aggregate trades into bars or derive any analytical measure.

## Fixtures, replay, CLI, and isolation

Representative and edge fixtures cover required numeric, condition, side, venue/scope, availability, sequence, lifecycle, duplicate, conflict, and cross-provider cases. The `TESTA` timeline contains original trade/quote receipt, later corrected trade receipt, and later cancelled quote receipt. The mixed fixture extends Phase 1H with independent `TRADES` and `QUOTES` while preserving all prior anchors.

`normalize-provider --provider trades-quotes`, `build-trade-quote-series`, `build-evidence`, and `build-evidence-timeline` accept local files only and emit stable JSON. Rejections return nonzero. Phase 1I adds no HTTP, FTP, WebSocket, SDK, credential, `.env`, token, database, GUI, order API, wall clock, random identity, pandas, NumPy, analytics dependency, depth book, synthetic NBBO, bar aggregation, aggressor classification, order-flow metric, spread/midpoint computation, liquidity/execution score, momentum, ranking, recommendation, or signal.

