# Phase 2V Outcome-Data Completion Amendment Design

## Purpose and boundary

This amendment adds an immutable historical-acquisition record and a separate,
deterministic outcome-analysis layer for BIYA. It does not alter the original Phase 2V
case, its fixture, its conclusion, or any Phase 1-2V anchor. It does not begin Phase 3A.

Historical outcome evidence cannot reconstruct missing original platform values. Later
market data can establish what BIYA did after the bounded detection period, but it cannot
recover the original price, percentage change, relative volume, short-float value,
days-to-cover value, news value, score, or label. Retrieval-time data must never be used
as though it existed at either original detection boundary.

## Architecture

The amendment has three explicit layers:

1. `scripts/acquisition/` performs controlled, one-shot provider access. Every attempt,
   including failure, writes a structured manifest. Raw acquisitions are immutable
   inputs and are never overwritten.
2. Additive `squeeze_core.validation.outcome_amendment_*` modules validate manifests,
   normalize supported raw records through existing Phase 1 adapters, and calculate
   retrospective observations. These modules are network-free and wall-clock-free.
3. A separate amendment case and public projection reference the original Phase 2V case
   without mutating it. Normalized derivatives remain separate from raw acquisitions.

The schema remains `1.0.0`. Existing models are not extended where doing so would change
prior serialized bytes. New deterministic identities reuse the established metric UUID
namespace with unique `result_type` discriminators.

## Acquisition evidence

An `AcquisitionManifest` records symbol, provider, data type, requested interval,
retrieval time, time zones, session scope, adjustment policy, sanitized request
parameters, result state, relative raw path, raw SHA-256, record count, observed range,
entitlement state, warnings, errors, limitations, and normalization linkage. Its ID is
stable for the complete acquisition event, including the explicit retrieval time.

Manifest result states distinguish success, partial response, empty response,
unavailable source, entitlement requirement, network failure, rate limit, unsupported
request, invalid response, and unknown failure. Provider failures and access limitations
remain explicit. A lower-priority fallback never erases a higher-priority failure.

No manifest may contain credentials, cookies, authentication parameters, account IDs,
absolute paths, personal data, or private provider URLs. Source provider configuration
and archived tokens remain byte-for-byte unchanged.

## Source order and current capability finding

Source order is fixed: existing local data, Interactive Brokers, existing Schwab
support, FINRA public data, existing/public news, then other stable public sources.

- The Phase 2V inventory and a fresh workspace search found no local BIYA market or
  event dataset.
- The archived application has IBKR support, but no configured local IBKR gateway is
  listening on ports 7497 or 4001 and the rebuilt environment has no IBKR SDK.
- The archived application has Schwab historical-price support and local token state.
  Calling it can refresh and rewrite archived tokens, which is prohibited. The attempt
  is therefore recorded as unavailable without loading, printing, or mutating secrets.
- FINRA public datasets are eligible for daily short-sale volume. This remains
  semantically separate from published short interest.
- Public historical market, news, halt, and corporate-action sources may be used only
  after the preceding limitations are recorded.

## Normalization

Supported market bars, news, halts, published short interest, borrow fee, and borrow
availability pass through the existing Phase 1 contracts and adapters. Normalized
observations preserve acquisition ID, raw hash, provider, source/effective/retrieval
timestamps, interval, session, units, adjustment status, quality, provenance, and
diagnostics. FINRA daily short-sale volume uses a separate additive evidence model; it
is never normalized as `PUBLISHED_SHORT_INTEREST`.

Duplicate records are diagnosed and emitted once. Same-identity conflicts remain
explicit and no winner is silently selected. Missing timestamps and incompatible units
reject normalization. Zero volume remains zero; missing volume remains missing. Partial
bars remain partial and their highs/lows carry an outcome limitation.

## Price comparability and sessions

BIYA completed a 1-for-10 reverse split effective for trading on 2026-07-13. The outcome
range begins after that effective date, but the daily context begins before it. The
acquisition and normalization layers therefore record whether provider prices are
adjusted or unadjusted and never mix the two in one return calculation. Any pre-split
daily context is descriptive unless the provider's adjustment basis is explicit.

Regular and extended-hours data remain distinguishable. No missing bar is interpolated,
forward-filled, or fabricated. No gap is inferred to be a halt without explicit halt
evidence.

## Boundary outcome policy

Both boundaries are always evaluated:

- `2026-07-17T14:23:58Z`
- `2026-07-17T16:54:58Z`

The reference policy is
`first_eligible_trade_bar_close_at_or_after_boundary.v1`. The first completed,
compatible bar whose start is at or after the boundary supplies the reference close.
No favorable intrabar low, assumed fill, later hindsight-selected entry, or maximum
price may be used as the reference.

For each boundary, the deterministic processor attempts 15 minutes, 30 minutes, one
hour, regular-session close, next regular-session open, next regular-session close, 24
hours, and maximum through dataset end. Each result records its requested and observed
range, reference, extrema, returns, adverse movement, time to extrema, volume, halt IDs,
missingness, and session coverage. No favorable-window selection is allowed.

## Interpretation and conclusion

Price movement, volume movement, halt activity, news timing, published short interest,
daily short-sale volume, borrow evidence, methodology validation, and causal
interpretation remain separate.

Price movement does not automatically prove a short squeeze. Daily short-sale volume is
not published short interest. A current borrow value is not historical borrow evidence.
No outcome model contains entry, exit, fill, P&L, position size, target, stop, score,
rank, recommendation, alert, or trading operation.

The amendment conclusion is exactly one of:

- `OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED` when retained historical market evidence
  objectively establishes a substantial subsequent move under the fixed policy; or
- `INSUFFICIENT_EVIDENCE` when outcome evidence is absent, incomplete, contradictory,
  adjustment-incompatible, or too limited.

The substantial-move rule is versioned and descriptive. It uses the same fixed windows
for both boundaries and cannot emit `VALIDATED_AS_RECORDED`, `PARTIALLY_VALIDATED`, or
`NOT_POINT_IN_TIME_VALID`. The original Phase 2V `INSUFFICIENT_EVIDENCE` conclusion
remains byte-identical; the amendment produces a separate updated result.

## Public projection and isolation

The public export is a whitelist projection containing only sanitized evidence needed
to explain the outcome. It excludes credentials, tokens, cookies, authentication
parameters, account identifiers, emails, phone numbers, local paths, and private URLs.
Filtering affects the generated public copy only and never source artifacts.

Deterministic validation and outcome code contains no provider call, HTTP client,
database write, GUI framework, trading API, order operation, random ID, wall-clock
identity, pandas, NumPy, SciPy, ML, sentiment, scoring, ranking, recommendation, or
alert. Tests require no live network.

