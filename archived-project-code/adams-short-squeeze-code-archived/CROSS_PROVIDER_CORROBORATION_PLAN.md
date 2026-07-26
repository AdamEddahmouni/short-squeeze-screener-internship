# Cross-Provider Corroboration — Handoff for Planning + Implementation

**Status: implemented and live-verified end-to-end, 2026-07-13.** All 6 open questions in §3 are
resolved and the design shipped - see `PROJECT_NOTES.md` §9d for the summary and `RESEARCH_LOG.md`'s
2026-07-13 corroboration entries for the full session log, including the live run with IB Gateway/
TWS connected that confirmed the "IB wins + Schwab corroborates" path fires correctly against real
data. This document is kept as-is below for the historical planning record.

**Written:** 2026-07-13, for a fresh session to pick up cold. Do not assume prior context —
everything needed to plan and implement this is below or linked. This is deliberately a *planning*
handoff, not a finished spec: several design decisions are called out as open and should be
either resolved by asking the user or made explicitly and documented, not silently assumed.

## 1. Why this exists — the advisor's own words

From an advisor call on 2026-07-12 (transcript reviewed 2026-07-13, logged in `RESEARCH_LOG.md`
§5): the advisor described his actual mental model for using this tool, and it is **not** "pick
whichever provider is connected" — it's cross-provider agreement as a trust signal:

> "...if TD Ameritrade is selling me [a signal]... if you are telling me from interactive broker
> [the same signal]... then we will know we have the right to invest in [it]... And if [there's]
> underlying activity, then I'm going to be there. I'm going to be looking into investment."

In plain terms: he wants to see when **IB and Schwab both independently flag the same ticker**
before treating a Prime/Subprime setup as trustworthy. A signal from only one provider is weaker
evidence than the same signal confirmed by both.

This directly conflicts with the current architecture (see §2), which only ever queries **one**
provider per cycle — the first available one in priority order. Building corroboration is a real
architectural change, not an additive tweak.

## 2. Current architecture — read this before touching anything

### 2.1 Provider dispatch (single-winner, not multi-source)

`app/ScreenerProject/controller/controller.py`:

- `DEFAULT_PROVIDER_PRIORITY = ["ib", "schwab", "finviz"]` (line 46), overridable via the
  `SCREENER_PROVIDER_PRIORITY` env var (comma-separated).
- `_provider_table()` (line 125) maps each name to `(source_name, is_available_fn, rank_and_group_fn)`.
- `_select_provider()` (line 143) walks the priority list and **returns the first available
  entry** — every other provider is never even called that cycle. This is the crux of what has
  to change: corroboration means calling more than one provider and comparing results, not
  picking a winner and ignoring the rest.
- `get_screener_results()` (line 194) calls `_select_provider()` once per 15-second cycle, then
  `rank_fn()` to get `(prime, subprime)` lists, then does news/sentiment matching and returns
  formatted rows for the GUI. `get_snapshot()` (further down) maps those same rows into the
  schema-v1 API contract.

### 2.2 The three provider modules — same contract, very different runtime models

All three of `ib_api.rank_and_group_stocks_ib()`, `schwab_api.rank_and_group_stocks_schwab()`,
and `filters.rank_and_group_stocks()` return `(prime: list[dict], subprime: list[dict])` where
every dict has the **identical key set** (this uniformity is intentional and load-bearing —
see `PROJECT_NOTES.md` §9c):

```
Ticker, Price, Float, RelVolume, ChangePercent, ShortFloat, Target, StopLoss, Headline,
SharesShort, DaysToCover, ShortInterestAsOf, ShortInterestSource, FloatAsOf, FloatSource,
IbShortableShares, IbShortableSharesAsOf,
SchwabHtbQuantity, SchwabHtbRate, SchwabIsHardToBorrow, SchwabHtbAsOf,
QualityFlags
```

Fields not applicable to a given provider are present as `None`, never omitted (e.g. Finviz rows
have `SharesShort: None`; IB/Finviz rows have all four `Schwab*` keys as `None`).

**But the two live providers work completely differently underneath, and this matters a lot for
corroboration design:**

- **`core/ib_api.py`** owns a persistent background thread + asyncio event loop
  (`start_ib_connection()`) that continuously runs IB's live scanner subscription and a 15-second
  enrichment loop, updating a module-level `_latest_snapshot` list in place. `rank_and_group_stocks_ib()`
  just reads whatever's currently in `_latest_snapshot` — it does **not** trigger a new fetch.
  Availability is `is_ib_available()`, which now also factors in enrichment health (see
  `PROJECT_NOTES.md` §7's "connection is no longer mistaken for usable data" fix) — connected but
  producing nothing for 3+ consecutive passes reports unavailable.
- **`core/schwab_api.py`** is stateless synchronous REST with short-lived OAuth tokens. There is
  **no background loop** — `rank_and_group_stocks_schwab()` calls `run_scan_cycle()` directly,
  which does one full movers → quotes → price-history round-trip **on demand, right then**.
  Availability is `is_available()`, a cheap local check (configured + unexpired refresh token),
  not a network probe.

Implication: today, calling `rank_and_group_stocks_schwab()` *in addition to* reading IB's
already-warm snapshot is not symmetric — it's an active new network round-trip every time, with
its own latency (movers + N quotes + N price-history calls) that could push a cycle past the 15s
target if done carelessly. A naive "just call both every cycle" needs to account for this
asymmetry (e.g. don't block IB's read waiting on Schwab's REST calls; consider running Schwab's
scan on its own thread/cadence rather than serially inside the same 15s tick).

### 2.3 Schema-v1 API / GUI

`controller.py`'s `get_snapshot()` maps the same `(ticker, price, ..., quality_flags)` positional
row tuple into the JSON contract served by `api_server.py`'s `/screener`. `ui/view.py`'s
`add_section()` renders the identical positional row into a `ttk.Treeview` with one column per
field (see the `columns = [...]` list around line 52). Any new corroboration field needs a slot in
**all three** places to stay consistent with how every other field in this codebase was threaded
through (see the short-interest and Schwab-HTB work for the exact pattern to copy: row dict →
`stock_data` dict in each `rank_and_group_stocks_*()` → `classify_batch()`'s row list →
`get_snapshot()`'s unpack/re-pack → `ui/view.py`'s `columns` list).

### 2.4 IB is genuinely live right now

As of 2026-07-13, IB Gateway/TWS is connected and working (verified via a full live
`python main.py` run), and the Schwab Trader API app is approved and OAuth-bootstrapped
(`core/schwab_auth.py` already run successfully, tokens cached in `data/schwab_tokens.json`,
gitignored). Both are real, both can be exercised live during implementation — this isn't
theoretical scaffolding anymore.

## 3. Open design questions — RESOLVED 2026-07-13

All six were resolved in a follow-up session: three by asking the user directly, three by
adopting this document's own reasoned defaults (confirmed rather than silently assumed).

1. **What counts as "the same signal"? — Resolved: graduated score, not a binary match.**
   The user's own framing: *"nothing HAS to match, but the more it does the more likely it is"* —
   corroboration is a confidence signal, not a pass/fail gate. Concretely: `rank_and_group_stocks_ib()`
   and `rank_and_group_stocks_schwab()` already score every ticker 0–4 against the identical rubric
   (price band $2–$20, change% ≥ 10, rel-vol ≥ 5, short-float ≥ 5% — see `core/ib_api.py` lines
   202–210 and `core/schwab_api.py`'s equivalent block; Prime = 4/4, Subprime = 3/4). Corroboration
   reuses this exact rubric rather than inventing new criteria: for each ticker IB flags as
   Prime/Subprime, fetch Schwab's quote for that ticker and recompute the same 0–4 score against
   Schwab's numbers. That score *is* the corroboration signal — no tier-match requirement, no
   separate threshold-matching logic.
2. **Gate vs label — Resolved: label only.** Confirmed by the user. A ticker IB flags still shows
   up in the GUI/API exactly as today; corroboration only adds metadata, never removes a row.
3. **Simultaneous availability / fallback — Resolved: yes, as originally proposed.** Corroboration
   is only attempted when IB is the selected provider for the cycle *and* `schwab_api.is_available()`
   is true. When Schwab isn't available, the new fields are simply absent/zero — today's
   single-provider behavior is otherwise completely unchanged, nothing is faked.
4. **New tier or new field — Resolved: new field.** Confirmed by the user. `setup_tier` stays
   `prime`/`subprime` unchanged. Add `CorroboratedBy` (list, e.g. `["schwab"]` — populated when
   Schwab's recomputed score ≥ 3, i.e. Schwab independently agrees this ticker is at least
   Subprime-worthy) and `CorroborationScore` (int 0–4, Schwab's recomputed score per point 1 above).
   Matches the `quality_flags` precedent for additive "list of signals" fields.
5. **Cadence/performance — Resolved: per-ticker check, not a broad scan.** Adopted this document's
   own recommendation. Never call Schwab's `fetch_movers()` for corroboration. Only call
   `schwab_api.fetch_quotes(tickers)` for the specific tickers IB already flagged that cycle (a
   handful, not the whole market), then apply the score in point 1. Cheap enough to run inline on
   the same 15s tick as IB's read — no independent timer needed.
6. **Finviz's role — Resolved: excluded entirely.** Adopted this document's own recommendation.
   Corroboration fields are always empty/absent when the winning provider is Finviz, or when IB
   wins but Schwab is unavailable. Corroboration is specifically an IB-vs-Schwab concept.

## 4. Suggested implementation sketch (a starting point, not a mandate)

Given §3.5's cost argument, the cheapest and most defensible design is likely:

1. Each cycle, get IB's current candidate list (already free — just reading `_latest_snapshot`).
2. For the tickers IB flagged as Prime/Subprime, fetch **just those tickers'** quotes from Schwab
   (`schwab_api.fetch_quotes(tickers)`, already exists) rather than running Schwab's own broad
   movers scan — this reuses existing, tested code and avoids a redundant full market scan.
3. Apply the same $2-$20 / change≥10% / relvol≥5 / short-float≥5% criteria to Schwab's numbers for
   those specific tickers (the scoring logic already exists in `rank_and_group_stocks_schwab()` —
   likely worth factoring the score-counting loop into a small shared helper both paths call,
   rather than duplicating it a third time).
4. Add a `corroborated_by` (or similar) field recording which provider(s) confirmed the signal.
5. This only makes sense when both `ib_api.is_ib_available()` and `schwab_api.is_available()` are
   true; single-provider mode should clearly not claim corroboration.

This sketch deliberately doesn't resolve §3's open questions (tier vs. field, gating vs. labeling)
— those still need a decision.

## 5. Files that will almost certainly need touching

- `controller/controller.py` — new corroboration logic, likely a new method alongside
  `_select_provider()`, wired into `get_screener_results()`/`get_snapshot()`.
- `core/ib_api.py` / `core/schwab_api.py` — possibly a small shared helper for the scoring-criteria
  check if it gets extracted (currently duplicated three times across
  `filters.rank_and_group_stocks()`, `ib_api.rank_and_group_stocks_ib()`,
  `schwab_api.rank_and_group_stocks_schwab()`).
- `ui/view.py` — new GUI column(s).
- Tests — this codebase has zero tolerance for untested new logic; see `tests/test_controller_snapshot.py`
  (stubs out `core.ib_api`/`core.schwab_api` as fake modules via `unittest.mock.patch.dict` +
  `types.ModuleType`, see the `_stubs` dict near the top) and `tests/test_schwab_api.py` for the
  established mocking patterns to follow.
- `PROJECT_NOTES.md` / `RESEARCH_LOG.md` — document the decision and design once made, following
  the existing §-numbered structure.

## 6. How this codebase verifies things — follow this pattern

This project does not consider "the mocked tests pass" sufficient on its own. Every feature this
session (2026-07-13) went through both offline tests **and** a live run:

```
cd app/ScreenerProject
python main.py
```

Then, in another shell: `curl http://127.0.0.1:8000/health` and `curl http://127.0.0.1:8000/screener`,
and inspect `data/screener_snapshot.json` directly. Three real bugs were caught this way today that
mocked tests alone did not catch (Schwab's `lastPrice` vs `last` field name, a dead-but-configured
Finviz key silently emptying news/sentiment, and yfinance's `.news` endpoint returning irrelevant
"trending" headlines) — full detail in `PROJECT_NOTES.md` §4/§7 and `RESEARCH_LOG.md`'s 2026-07-13
entries. **Do the same for this feature**: build it, write offline tests, then actually run
`main.py` live against the real IB connection and the real approved Schwab account and confirm
corroboration fires correctly on genuine live data before calling it done.

Notes on the live environment from today's session, since they'll likely recur:
- Port 8000 can be held by an unrelated process on this machine; check with
  `netstat -ano | grep ":8000"` before assuming a bind failure is our own code's fault.
- On Windows/MSYS bash, `ps -W`'s columns are PID, PPID, PGID, **WINPID**, TTY, UID, STIME,
  COMMAND — use the WINPID column with `taskkill //PID <winpid> //F`, not the MSYS-space PID.
- IB error 10089 ("delayed market data available") on individual symbols is expected/harmless on
  this account (no paid real-time entitlement) — it is not a connection failure.

## 7. What NOT to do

- Don't silently fold this into `ib_shortable_shares` or any existing field — it's a new concept
  (agreement between providers), not another provider-specific data point.
- Don't make Finviz part of corroboration (§3.6).
- Don't have Schwab's corroboration check trigger a full `fetch_movers()` scan if the cheaper
  "check IB's already-flagged tickers against Schwab's quotes" design (§4) is adopted instead —
  that would double network cost for no added benefit.
- Don't skip the live verification step (§6) — this codebase's own recent history shows offline
  tests alone missed real bugs twice in one session.
