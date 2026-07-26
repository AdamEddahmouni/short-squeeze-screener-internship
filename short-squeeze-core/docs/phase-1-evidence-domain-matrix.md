# Phase 1 Evidence-Domain Matrix

Human-readable companion to the machine-readable
[`phase-1-evidence-domain-matrix.json`](phase-1-evidence-domain-matrix.json). The JSON is the
authoritative source and is cross-checked against the code by
`tests/compatibility/test_phase_1_domain_matrix.py` (domains equal `CoverageDomain`; every
event/payload triple equals `PAYLOAD_BINDINGS`; provider modules import; referenced docs exist).

## Domain → contract map

| Coverage domain | Event type | Payload model | Phase | Provider module |
| --- | --- | --- | --- | --- |
| CANDIDATE_SNAPSHOT | MARKET_SNAPSHOT | MarketSnapshotPayload | 1C | adapters.finviz |
| BORROW_FEE | BORROW_FEE | BorrowFeePayload | 1B | adapters.ibkr |
| BORROW_AVAILABILITY | BORROW_AVAILABILITY | BorrowAvailabilityPayload | 1B | adapters.ibkr |
| PUBLISHED_SHORT_INTEREST | PUBLISHED_SHORT_INTEREST | PublishedShortInterestPayload | 1D | adapters.finra |
| SEC_FILINGS | SEC_FILING | SecFilingPayload | 1E | adapters.sec |
| TRADING_HALTS | TRADING_HALT | TradingHaltPayload | 1F | adapters.halts |
| NEWS | NEWS_ITEM | NewsItemPayload | 1G | adapters.news |
| MARKET_BARS | BAR | BarPayload | 1H | adapters.market_bars |
| TRADES | TRADE | TradePayload | 1I | adapters.trades_quotes |
| QUOTES | QUOTE | QuotePayload | 1I | adapters.trades_quotes |

Terminology note: the coverage domain `CANDIDATE_SNAPSHOT` is carried by the canonical event
type `MARKET_SNAPSHOT`. This is the one place where the coverage-domain name and the event-type
name differ; every other domain shares its name with its event type.

## Shared point-in-time model

Every domain enforces the same availability gates against `as_of`:

1. **Provider/public availability** (`source_timestamp`) ≤ `as_of` — enforced for the
   publication-gated domains (short interest, SEC, halts, news, bars, trades, quotes). The
   Phase 1B/1C borrow and snapshot domains use effective time as their availability proxy.
2. **Local receipt** (`received_timestamp`) ≤ `as_of` — enforced for **every** domain, never
   relaxed by `maximum_future_skew_ms`.
3. **Effective time** (`effective_timestamp`) ≤ `as_of + maximum_future_skew_ms`.
4. **Non-future event time** — trades and quotes additionally exclude any record whose provider
   `event_timestamp` is after `as_of`, so event time alone never creates eligibility.

`tests/compatibility/test_phase_1_release_candidate.py` proves gates 1–4 uniformly across all ten
domains. Represented event time (settlement date, period of report, halt/resume time, bar_end,
event_timestamp) never substitutes for availability.

## Age dimensions per domain

Each domain reports `availability_age_ms`; publication-gated domains add domain-specific ages
(reporting-period, filing, announcement, halt/resumption event, publication, capture, interval,
update, event, correction). All ages are non-negative integer milliseconds/days derived purely
from `as_of` minus a structured timestamp — no wall clock is consulted.

## Duplicate / conflict / revision behavior

No domain averages sources, silently selects a winner, overwrites changed content, converts
missing evidence into neutral evidence, or treats a temporal difference as a direct conflict.
Conflicts carry deterministic `conflict-<hash>` identities and stable ordering; revisions and
news relationships carry deterministic identities. Later lifecycle records never mutate earlier
observations or earlier bundles. See
[`phase-1-lifecycle-consistency.md`](phase-1-lifecycle-consistency.md).

## Per-domain detail

Full per-domain records (objective fields, timestamp semantics, unknown-availability policy,
coverage states, age dimensions, duplicate/conflict/revision behavior, point-in-time selector,
fixture families and provenance, CLI commands, documentation, and known limitations) are in the
JSON matrix. Each domain's provider documentation and ADRs are linked from the JSON `documentation`
field.
