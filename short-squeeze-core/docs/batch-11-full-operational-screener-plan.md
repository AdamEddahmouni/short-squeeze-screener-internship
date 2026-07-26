# Batch 11 — Full Operational Live Research Screener (preregistration)

Branch: `batch/full-operational-live-screener-11`
Parent: `a399e4f3bff4d0ddcae57eefe68073cd0543a92d` (Batch 10)
Type: application / integration. **Not** Phase 3E. No trading, no account access.

Written before implementation. Deviations are recorded in the completion report.

## 1. Objective

Batch 10 delivered a truthful frozen-research viewer with a manual-symbol current mode in
which every rule was `UNKNOWN`. Batch 11 makes the current mode an actual screener:
automatic discovery, auto-refresh, current charting, and a **real Phase 3A evaluation over
current evidence** using the existing canonical pipeline.

Functionality expands. Evidence standards do not move.

## 2. Non-negotiable invariants

* No canonical registry, Batch 05 raw artifact, Batch 08 freeze, or Batch 09 preview is
  read for mutation or written. Current mode is ephemeral, in-memory, export-only.
* No forward window, no outcome, no prediction, no score, no rank, no target/stop.
* Missing evidence is never zero, never defaulted, never inferred. `UNKNOWN` is a result.
* No order method, no account method. Enforced by a new static guard (§7).
* Frozen Research mode never depends on a live provider.

## 3. Current discovery is separate from the frozen cohort

A discovered symbol becomes a `CurrentDiscoveryCandidate`: an application-session object.
It is not a Batch 01 case, carries no `case_id`, is never outcome-labelled, and never
enters a research registry. Historical statistics and current statistics are reported in
two separate panels and are never summed.

Label used throughout: **CURRENT DISCOVERY — EXPERIMENTAL RESEARCH SCREEN**.

## 4. Provider surface (read-only, official local IBKR API only)

Permitted: `reqCurrentTime`, `reqContractDetails`, `reqHistoricalData`,
`cancelHistoricalData`, `reqScannerParameters`, `reqScannerSubscription`,
`cancelScannerSubscription`, `reqMarketDataType`, `reqMktData`, `cancelMktData`.

Forbidden, guard-enforced: every order, account, position, execution, PnL and portfolio
method, and every order object.

The Batch 05 research exporter (`tools/ibkr_historical_export`) is **not** modified — its
narrow guard keeps forbidding scanner and market-data methods. The application owns a
separate session subclass and a separate guard with the wider read-only allowance.

### 4.1 Discovery profiles

| Profile | Scanner configuration | Rationale |
|---|---|---|
| `BROAD_MOVERS` | `instrument=STK`, `locationCode=STK.US.MAJOR`, `scanCode=TOP_PERC_GAIN` | Active US movers, no rubric assumption. |
| `MOST_ACTIVE` | same, `scanCode=MOST_ACTIVE` | Volume-active names, provider ordering only. |
| `HISTORICAL_RUBRIC_LIKE` | `TOP_PERC_GAIN` plus `abovePrice=2`, `belowPrice=20` read from the committed `PRICE_RANGE` thresholds | Approximates the original workflow using *policy* numbers, not invented ones. |
| `MANUAL_SYMBOL` | no scanner; user-entered tickers | Batch 10 behaviour, preserved. |

Ordering shown as **Provider scanner order**, never as a rank. Each profile displays its
exact criteria in the UI.

## 5. Current Phase 3A evaluation

No new rule, no new formula, no new evaluator. The current adapter:

1. pulls trailing 1-minute bars via `reqHistoricalData`;
2. keeps only bars **definitely completed** under both timestamp interpretations
   (`label + interval <= as_of`) — the Batch 07 bidirectional envelope;
3. normalises them with `squeeze_core.adapters.market_bars.normalize_market_bar_records`,
   **omitting volume** (unit and corporate-action semantics remain UNRESOLVED per Batch 06);
4. computes `PERCENTAGE_RETURN` through `squeeze_core.metrics.returns.build_return_result`
   (earliest → latest definitely-completed close), the same canonical call the Batch 08
   metric adapter uses;
5. builds the three readiness records through the existing Phase 2D builders;
6. builds an ordinary `RuleEvaluationRequest`;
7. runs `squeeze_core.evaluation.evaluator.evaluate_candidate` against the committed
   25-rule policy.

### 5.1 The one deliberate difference from the frozen request

`provider_scope = ("IBKR",)` in current mode; the Batch 08 frozen request uses `()`.

Justification, per §16 of the batch brief: the Batch 07 absolute-price block exists because
Batch 06 resolved the provider price series as **split-adjusted**, so a level recorded at a
*past* boundary may have been restated by a corporate action occurring between that boundary
and retrieval. For a bar completed inside the **current** session with `as_of` at that same
instant, no such interval exists — the adjusted level and the contemporaneous traded level
coincide. The absolute level of the latest definitely-completed current bar is therefore
admissible **as a current price level only**.

Consequence: `PRICE_RANGE` and `PROVIDER_SCOPE_EXPLICIT` become evaluable in current mode.
`FLOAT_MAXIMUM`, `PUBLISHED_SHORT_INTEREST_AVAILABLE`, `BORROW_FEE_MINIMUM` and
`BORROW_AVAILABILITY_MAXIMUM` gain scope but still have no evidence, so they stay `UNKNOWN`
for the honest reason rather than the scope reason.

The historical determination is untouched. Frozen mode is byte-for-byte unchanged and its
request keeps `provider_scope = ()`.

### 5.2 What stays UNKNOWN, and why

* `RELATIVE_VOLUME_MINIMUM` — provider volume unit and corporate-action treatment remain
  UNRESOLVED (Batch 06). Raw volume may be *displayed* with an explicit
  `UNRESOLVED_PROVIDER_UNIT` label but never enters evidence.
* Float, published short interest, days to cover, borrow fee, borrow availability and their
  change rules — no configured provider.
* News / SEC / corporate action — no configured provider unless §6 lands.

## 6. Provider-backed extras (best effort, P1)

Attempted only where a real provider exists tonight; otherwise the panel reports
`NOT CONFIGURED` and stays operational.

* IBKR shortability / fee ticks (generic ticks `236` shortable, `456` dividends): implemented
  only if the gateway actually returns them under the user's entitlement; otherwise
  `PERMISSION_UNAVAILABLE`, never `0`.
* News: only through a lawfully configured provider. The archived Finviz TLS-impersonation
  helper is excluded. FinBERT sentiment is deferred unless P0 lands with time to spare.

## 7. Read-only guard

`apps/research_screener/guard.py` scans the application package for forbidden method and
object names and is asserted by a committed test. The UI is scanned for `Buy` / `Sell` /
`Place Order` / `Trade Now` action controls.

## 8. Refresh model

* Quote/evidence refresh: 30 s default, configurable, provider-paced.
* Scanner refresh: 180 s default.
* A failed refresh **retains** the previous snapshot and marks it `STALE` with the error.
* Rule-outcome transitions (`UNKNOWN → PASS`) are recorded as *research-state changes*,
  never as "signal triggered".
* Bounded session history: last 100 snapshots per symbol, in memory only.

## 9. Startup

UI is served before any provider is touched. Frozen data loads from local artifacts.
`DEMO READY` requires only: server up, frozen artifacts loaded, 13 results present,
integrity checks passed. `LIVE SOURCES READY` is reported separately. Target: frozen UI
usable in under ~5 s with the gateway closed.

## 10. Endpoints

`/api/health`, `/api/providers`, `/api/frozen/candidates`, `/api/frozen/candidate`,
`/api/live/candidates`, `/api/live/candidate`, `/api/live/refresh`,
`/api/discovery/refresh`, `/api/discovery/profiles`, `/api/professor`, `/api/export`.
The Batch 10 routes (`/api/screener`, `/api/symbol`) are retained.

## 11. Tests

Focused, synthetic-provider only. The suite must not require a live gateway. Coverage:
discovery with a synthetic scanner, scanner failure degradation, candidate identity
stability, quote update, market-data-type labelling, auto-refresh, stale retention, current
chart, current Phase 3A invocation, `PRICE_RANGE` admissibility, canonical metric use,
volume staying `UNKNOWN`, short-pressure staying `UNKNOWN`, news `NOT CONFIGURED`, 25 rules
visible, transition history, current export, no missing→zero conversion, reconnect, frozen
mode unaffected, Batch 08 unchanged, canonical Phase 3B unchanged, no forward read, no
orders, no account access, startup with gateway down.

## 12. Definition of done

As §47 of the batch brief. Anything not achieved is reported explicitly as not achieved.
