import asyncio
import os
import statistics
import threading
import time
from collections import deque
from datetime import datetime, timezone

from ib_async import IB, ScannerSubscription
from dotenv import load_dotenv

from core.filters import compute_target_stop
from core.finnhub_api import fetch_finnhub_price
from core.ib_borrow_rate import get_borrow_rate_async as _get_borrow_rate
from core.provider_utils import epoch_to_iso_date as _epoch_to_iso_date, is_valid_number as _is_valid_number
from core.short_interest import (
    calculate_days_to_cover,
    calculate_short_float_percent,
    check_short_float_discrepancy,
)
from core.technical_indicators import (
    compute_rsi as _compute_rsi,
    compute_weekly_volatility as _compute_weekly_volatility,
    compute_ttm_squeeze as _compute_ttm_squeeze,
)
from core.yfinance_float_api import get_float_stats_async as _get_float_stats

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def _env_int(name, default):
    """Read an integer setting, falling back for blank or malformed values."""
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


# Connection target, overridable per-machine via .env (IB_HOST/IB_PORT/IB_CLIENT_ID) so a
# team member can point this at their own Gateway/account without editing source - defaults
# match this project's original single-account setup (paper/live Gateway on the default port).
IB_HOST = os.environ.get("IB_HOST") or "127.0.0.1"
IB_PORT = _env_int("IB_PORT", 4001)
IB_CLIENT_ID = _env_int("IB_CLIENT_ID", 7)

# --- v1 constants, confirmed against a live Gateway session (2026-07-08) ---
# "TOP_PERC_GAIN" and "STK.US.MAJOR" verified valid via a live reqScannerParameters()
# call - IB's actual scan code is TOP_PERC_GAIN, not the more guessable "TOP_PCT_GAIN".
SCAN_CODE = "TOP_PERC_GAIN"
LOCATION_CODE = "STK.US.MAJOR"
SCANNER_ROWS = 50

# Historical-bar cache TTL for RSI/weekly-volatility/average-volume/TTM Squeeze - the *nominal*
# freshness target, not the actual safety mechanism. _hist_rate_limit_allows() below is what
# actually keeps reqHistoricalData calls under IB's documented ~60-req/10-min pacing limit; this
# TTL just controls how eagerly a symbol is considered "worth refreshing" once budget is
# available. Real achieved freshness settles around 5-10 min under realistic scanner load (50
# tickers, churn staggers when each goes stale) - shortened from 1hr 2026-07-17 once the rate
# limiter below made it safe to.
HIST_CACHE_TTL_SECONDS = 300

# Deliberately below IB's documented "~60" (not exactly 60) - the "~" means the real enforcement
# point isn't precisely specified, and a small margin costs almost nothing in freshness.
_HIST_RATE_LIMIT_MAX_CALLS = 55
_HIST_RATE_LIMIT_WINDOW_SECONDS = 600

# Target start-to-start cadence for the tick-236/price enrichment pass, decoupled from how often
# the scanner itself pushes updates. A normal cached 50-row pass spends about 10s settling five
# market-data batches, leaving headroom inside this 15s target. Slow first-run cache fills can take
# longer; in that case the next pass starts immediately instead of adding another fixed delay.
ENRICH_INTERVAL_SECONDS = 15

# reqMktData batching to stay under IB's per-connection pacing limits - never hold
# more than one batch's market-data lines open at once.
BATCH_SIZE = 10
BATCH_SETTLE_SECONDS = 2.0

# Basic reconnect handling (v1 scope, not a production watchdog): fixed backoff,
# capped attempts. Real IB-side connectivity blips (Error 1100/1102) were observed
# live during testing without this - the app just silently stayed on the Finviz
# fallback until the process was restarted.
RECONNECT_BACKOFF_SECONDS = 10
MAX_RECONNECT_ATTEMPTS = 5

# A few transient enrichment failures (a bad batch, a rate-limit blip) shouldn't flip
# controller.py's provider dispatch away from IB, but a session that's connected yet
# structurally unable to produce rows should - otherwise a connected-but-broken IB session
# would keep winning over Schwab/Finviz forever. Mirrors MAX_RECONNECT_ATTEMPTS's "bounded, not
# infinite" philosophy.
MAX_CONSECUTIVE_ENRICHMENT_FAILURES = 3

# --- module-level state ---
_state_lock = threading.Lock()
_connected = False
_latest_snapshot = []  # list of enriched per-ticker dicts, see _enrich_rows()
_consecutive_enrichment_failures = 0

_raw_scan_lock = threading.Lock()
_raw_scan_rows = []  # latest raw ScanData rows from the live subscription

_hist_cache = {}  # symbol -> (fetched_at_epoch, {"rsi", "vol_w", "avg_volume"})
_hist_request_times = deque()  # epoch timestamps of reqHistoricalData call attempts, oldest-first
# Float/short-interest cache lives in core/yfinance_float_api.py, shared with core/schwab_api.py.

_thread_lock = threading.Lock()
_started = False
_loop = None
_ib = None
_reconnecting = False  # guards against overlapping reconnect attempts
_shutting_down = False  # set by stop_ib_connection() so its disconnect doesn't trigger a reconnect

# Connection params, stashed at start_ib_connection() time so a reconnect attempt
# can reuse them without them needing to be threaded through every callback.
_host = None
_port = None
_client_id = None


# Starts the background IB thread/event loop/connection if not already running.
# Idempotent and non-blocking - safe to call from Controller.__init__ without
# freezing the Tk window while Gateway connects.
def start_ib_connection(host=IB_HOST, port=IB_PORT, client_id=IB_CLIENT_ID):
    global _started, _host, _port, _client_id
    with _thread_lock:
        if _started:
            return
        _started = True
        _host, _port, _client_id = host, port, client_id
        thread = threading.Thread(
            target=_run_ib_thread, args=(host, port, client_id), daemon=True
        )
        thread.start()


# Thread-safe check controller.py's provider dispatch (_select_provider()) uses to decide
# whether IB is usable this cycle. True only if IB is connected AND its enrichment pass is
# actually producing data - a connected-but-structurally-broken session (e.g. every row failing
# to build, see _record_enrichment_result()) must not block falling through to Schwab/Finviz.
def is_ib_available():
    with _state_lock:
        return _connected and _consecutive_enrichment_failures < MAX_CONSECUTIVE_ENRICHMENT_FAILURES


# Records whether an enrichment pass actually produced usable rows. IB handing us raw scanner
# candidates that all fail to enrich is a real health signal; IB handing us nothing to enrich at
# all (rows was empty) never reaches this function, so it's not conflated with "genuinely zero
# matches this cycle" (see rank_and_group_stocks_ib()'s docstring for why an empty *scored*
# result is still valid - this is a level below that, about raw enrichment, not final scoring).
def _record_enrichment_result(enriched_count):
    global _consecutive_enrichment_failures
    with _state_lock:
        _consecutive_enrichment_failures = 0 if enriched_count > 0 else _consecutive_enrichment_failures + 1


def _record_enrichment_exception():
    global _consecutive_enrichment_failures
    with _state_lock:
        _consecutive_enrichment_failures += 1


def _reset_enrichment_failures():
    global _consecutive_enrichment_failures
    with _state_lock:
        _consecutive_enrichment_failures = 0


# Requests a graceful shutdown of the IB connection/thread. Safe to call even if
# the connection never started or already dropped. Marks this as intentional so
# _on_disconnected() doesn't try to reconnect right as the app is closing.
def stop_ib_connection():
    global _shutting_down
    _shutting_down = True
    loop = _loop
    ib = _ib
    if loop is not None and loop.is_running() and ib is not None:
        asyncio.run_coroutine_threadsafe(_disconnect(ib), loop)


async def _disconnect(ib):
    ib.disconnect()


# Same output shape as core/filters.py's get_filtered_stocks().
def get_filtered_stocks_ib():
    with _state_lock:
        snapshot = list(_latest_snapshot)

    return [
        {
            "Ticker": s["ticker"],
            "Price": s["price"],
            "Float": s["float_shares"],
            "RelVolume": s["rel_volume"],
            "ChangePercent": s["change_percent"],
            "Headline": None,
        }
        for s in snapshot
    ]


# Same output shape as core/filters.py's rank_and_group_stocks(): a flat list of candidate
# dicts, not pre-split into Prime/Subprime. Float isn't available from IB itself without a
# market-data-fundamentals subscription (verified: reqFundamentalData returns error 10358 "not
# allowed" on this account) - _build_row() works around that for free via yfinance's .info
# endpoint (see FLOAT_CACHE_TTL_SECONDS above) rather than IB, so it's display-only here, not a
# classification criterion (same as the Finviz path, which pre-filters to float<20M at the query
# level - sh_float_u20 in finviz_api.py's URL - rather than scoring it). Tier classification
# itself (2026-07-17 redesign, SQUEEZE_FORMULA_REDESIGN_HANDOFF.md) now happens once, cross-
# provider, in controller.py via core/squeeze_score.py::classify_tier() off the composite squeeze
# score - not here via core/scoring.py::score_setup(), which is no longer called from this
# function (its only remaining caller is core/schwab_api.py's corroboration rescoring).
def rank_and_group_stocks_ib():
    with _state_lock:
        snapshot = list(_latest_snapshot)

    candidates = []
    for s in snapshot:
        target, stop = compute_target_stop(s["_vol_w"], s["_rsi"])

        stock_data = {
            "Ticker": s["ticker"],
            "Price": s["price"],
            "Float": s["float_shares"],
            "RelVolume": s["rel_volume"],
            "ChangePercent": s["change_percent"],
            "ShortFloat": s["short_float_percent"],
            "Target": target,
            "StopLoss": stop,
            "Headline": None,
            "SharesShort": s.get("shares_short"),
            "DaysToCover": s.get("days_to_cover"),
            "ShortInterestAsOf": s.get("short_interest_as_of"),
            "ShortInterestSource": s.get("short_interest_source"),
            "FloatAsOf": s.get("float_as_of"),
            "FloatSource": s.get("float_source"),
            "IbShortableShares": s.get("ib_shortable_shares"),
            "IbShortableSharesAsOf": s.get("ib_shortable_shares_as_of"),
            # Schwab-only field (its /quotes hard-to-borrow signal, see core/schwab_api.py) -
            # kept present as None here too so every provider's row has an identical key set.
            "SchwabHtbQuantity": None,
            "SchwabHtbRate": None,
            "SchwabIsHardToBorrow": None,
            "SchwabHtbAsOf": None,
            # TTM Squeeze (core/technical_indicators.py::compute_ttm_squeeze()) - display-only
            # volatility-compression signal, computed from the same daily bars already fetched
            # for RSI/weekly-volatility above, not a new API call.
            "TtmSqueezeOn": s.get("ttm_squeeze_on"),
            "TtmSqueezeMomentum": s.get("ttm_squeeze_momentum"),
            # IB's own indicative stock-loan borrow cost (core/ib_borrow_rate.py) - IB-only, like
            # ib_shortable_shares above; other providers get None (see core/schwab_api.py,
            # core/filters.py) rather than a fabricated value.
            "IbBorrowFeeRate": s.get("ib_borrow_fee_rate"),
            "IbBorrowRebateRate": s.get("ib_borrow_rebate_rate"),
            "IbBorrowRateAsOf": s.get("ib_borrow_rate_as_of"),
            "QualityFlags": s.get("quality_flags", []),
        }

        candidates.append(stock_data)

    return candidates


def _run_ib_thread(host, port, client_id):
    global _loop, _ib

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _loop = loop

    ib = IB()
    _ib = ib
    ib.disconnectedEvent += _on_disconnected

    loop.run_until_complete(_connect_and_subscribe(ib, host, port, client_id))
    try:
        loop.run_forever()
    finally:
        loop.close()


async def _connect_and_subscribe(ib, host, port, client_id):
    global _connected

    try:
        await ib.connectAsync(host, port, clientId=client_id, timeout=15)
    except Exception as e:
        print(f"⚠️ IB connection failed: {e}")
        return

    _configure_and_subscribe(ib)

    with _state_lock:
        _connected = True
    _reset_enrichment_failures()  # fresh connection deserves a fresh chance, not a stale count

    asyncio.ensure_future(_enrichment_loop(ib))


# Re-applies market data type and (re-)establishes the scanner subscription.
# Shared by the initial connect and the reconnect path so neither duplicates it.
def _configure_and_subscribe(ib):
    # Request live data as the preferred type - IB auto-substitutes delayed
    # data per-symbol if a specific instrument isn't entitled, so this is safe
    # even without full real-time entitlement. Previously hardcoded to 3
    # (delayed) based on a since-corrected assumption that this account had no
    # real-time entitlement at all (error 10089 without *any* type set) - IB's
    # Client Portal (Market Data Subscriptions, checked 2026-07-09) shows this
    # account already carries a $0/"Fee Waived" "US Real-Time Non Consolidated
    # Streaming Quotes" entitlement (BATS/BYX/EDGX/EDGEA/IEX), which type 3 was
    # discarding by forcing delayed mode regardless. Tick 236 (shortable
    # shares) is unaffected either way.
    ib.reqMarketDataType(1)

    subscription = ScannerSubscription(
        numberOfRows=SCANNER_ROWS,
        instrument="STK",
        locationCode=LOCATION_CODE,
        scanCode=SCAN_CODE,
        abovePrice=2.0,
        belowPrice=20.0,
    )
    scan_data = ib.reqScannerSubscription(subscription)
    scan_data.updateEvent += _on_scan_update


# Fires on any disconnect (initial drop or a failed reconnect attempt's own
# disconnect). Flips availability off immediately (routing controller.py back to
# the Finviz fallback) and kicks off a bounded, backed-off reconnect attempt.
def _on_disconnected():
    global _connected, _reconnecting
    with _state_lock:
        _connected = False

    if not _reconnecting and not _shutting_down:
        _reconnecting = True
        asyncio.ensure_future(_reconnect_loop())


# Basic reconnect handling (v1 scope, not a production watchdog): fixed backoff,
# capped attempts, reusing the same IB() instance and stashed connection params.
# On success, re-applies market data type and re-subscribes the scanner (the old
# subscription is dead once disconnected). On exhausting all attempts, gives up
# and leaves the connection unavailable for the rest of this run - controller.py's
# provider-priority dispatch (_select_provider()) falls through to Schwab, then
# Finviz, rather than retrying forever against a dead Gateway. IB itself never
# reconnects again after this within the same process; restart the app once
# Gateway is back up to resume using it.
async def _reconnect_loop():
    global _connected, _reconnecting

    for attempt in range(1, MAX_RECONNECT_ATTEMPTS + 1):
        await asyncio.sleep(RECONNECT_BACKOFF_SECONDS)
        print(f"IB reconnect attempt {attempt}/{MAX_RECONNECT_ATTEMPTS}...")

        try:
            await _ib.connectAsync(_host, _port, clientId=_client_id, timeout=15)
            _configure_and_subscribe(_ib)
            with _state_lock:
                _connected = True
            _reset_enrichment_failures()
            print("IB reconnected.")
            _reconnecting = False
            return
        except Exception as e:
            print(f"⚠️ IB reconnect attempt {attempt} failed: {e}")

    print(f"⚠️ IB reconnect gave up after {MAX_RECONNECT_ATTEMPTS} attempts; falling through to Schwab/Finviz for the "
          "rest of this run. Restart the app once IB Gateway is back up to resume using it.")
    _reconnecting = False


# Stores the latest raw scan rows for the enrichment loop to pick up on its own
# cadence - deliberately decoupled from however often IB pushes scanner updates,
# since the tick-236 enrichment pass has its own pacing constraints (see below).
def _on_scan_update(scan_data_list):
    with _raw_scan_lock:
        _raw_scan_rows.clear()
        _raw_scan_rows.extend(scan_data_list)


async def _enrichment_loop(ib):
    while True:
        pass_started_at = time.monotonic()
        with _raw_scan_lock:
            rows = list(_raw_scan_rows)

        # Skip enrichment while disconnected/reconnecting - reqMktData/reqHistoricalData would
        # just fail with "Not connected" until the reconnect loop (see _on_disconnected) succeeds
        # or gives up. Checks the raw _connected flag directly, not is_ib_available() - that
        # function also factors in enrichment health (see _record_enrichment_result()), and using
        # it here would make a struggling session stop even trying to recover.
        with _state_lock:
            connected = _connected

        if rows and connected:
            try:
                enriched = await _enrich_rows(ib, rows)
                with _state_lock:
                    _latest_snapshot.clear()
                    _latest_snapshot.extend(enriched)
                _record_enrichment_result(len(enriched))
            except Exception as e:
                print(f"⚠️ IB enrichment pass failed: {e}")
                _record_enrichment_exception()

        elapsed = time.monotonic() - pass_started_at
        await asyncio.sleep(max(0, ENRICH_INTERVAL_SECONDS - elapsed))


# Batches contracts to stay under IB's reqMktData pacing limits: request a small
# batch, let ticks settle, read what's populated, cancel, move to the next batch -
# never more than BATCH_SIZE market-data lines open at once.
async def _enrich_rows(ib, rows):
    results = []

    for batch_start in range(0, len(rows), BATCH_SIZE):
        batch = rows[batch_start:batch_start + BATCH_SIZE]
        contracts = [row.contractDetails.contract for row in batch]

        tickers = [ib.reqMktData(c, genericTickList="236") for c in contracts]
        await asyncio.sleep(BATCH_SETTLE_SECONDS)

        # Historical-data lookups (cache misses) are the slow part of a row build,
        # so fan them out concurrently within the batch rather than one at a time -
        # 10-way concurrency across distinct contracts is well within IB's pacing
        # guidance (the hard limit is on repeated requests for the *same* contract).
        row_results = await asyncio.gather(
            *(_build_row(ib, contract, ticker) for contract, ticker in zip(contracts, tickers)),
            return_exceptions=True,
        )
        for row_data in row_results:
            if isinstance(row_data, Exception):
                print(f"⚠️ IB row enrichment failed: {row_data}")
            elif row_data is not None:
                results.append(row_data)

        for c in contracts:
            ib.cancelMktData(c)

    return results


# Used when reqHistoricalData genuinely fails (see _get_hist_stats()) - RSI/weekly-volatility/
# relative-volume can't be computed without bars, but that alone must not discard the whole row:
# price/change% can still come from the live tick or Finnhub, which is why _build_row() no longer
# hard-returns None just because history failed (FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md §4
# defect #1).
_DEGRADED_HIST_STATS = {
    "vol_w": 0.0, "rsi": 50.0, "avg_volume": None, "last_volume": None,
    "last_close": None, "prev_close": None,
    "ttm_squeeze_on": None, "ttm_squeeze_momentum": None,
}


def _hist_stats_or_degraded(hist):
    """Returns (stats, is_degraded). is_degraded is True only when reqHistoricalData failed and
    these placeholder values are standing in for it."""
    if hist is not None:
        return hist, False
    return dict(_DEGRADED_HIST_STATS), True


async def _build_row(ib, contract, ticker):
    hist, historical_data_missing = _hist_stats_or_degraded(await _get_hist_stats(ib, contract))

    # Price fallback chain: IB's own tick first - now that _configure_and_subscribe()
    # requests live data (type 1) instead of forcing delayed (type 3), this is real-time
    # for this account's entitled feed (PROJECT_NOTES.md §8, confirmed via Client Portal
    # 2026-07-09), not the ~15-20min-delayed data it used to be. Finnhub's free-tier quote
    # is now only a last-resort backup for the rare case IB's own tick is transiently
    # unavailable (-1/NaN observed live outside market hours) - it moved from primary to
    # fallback after real use showed the free tier's 60/min cap gets hit almost immediately
    # at this app's actual scanner volume (SCANNER_ROWS=50), and after the advisor flagged
    # non-free-tier Finnhub pricing/latency concerns for anything beyond that cap. Most
    # cycles should now resolve via IB alone, so Finnhub calls (and its rate limit) should
    # rarely even trigger. Most recent historical close remains the final fallback either way.
    price = ticker.last if _is_valid_number(ticker.last) and ticker.last > 0 else None
    if price is None:
        price = await asyncio.to_thread(fetch_finnhub_price, contract.symbol)
    if price is None:
        price = hist["last_close"]
    if price is None:
        return None  # no price from any source (live tick, Finnhub, or historical close)

    prev_close = ticker.close if _is_valid_number(ticker.close) and ticker.close > 0 else hist["prev_close"]
    if not prev_close:
        return None  # can't compute change% without any prev_close source

    change_percent = round(((price - prev_close) / prev_close) * 100, 2)

    # Live intraday volume ticks proved unreliable in delayed mode during testing
    # (returned 0/NaN); use the most recent historical bar's volume as the
    # "today" proxy against the historical average instead. Both are None when
    # historical_data_missing - relative volume genuinely can't be computed without bars.
    today_volume = hist["last_volume"]
    if today_volume is not None and hist["avg_volume"]:
        rel_volume = round(today_volume / hist["avg_volume"], 2)
    else:
        rel_volume = 0.0

    # None (not 0) when IB doesn't report the field - 0 shortable shares is a real, meaningful
    # signal (completely hard to borrow) and must not be confused with "IB didn't tell us."
    shortable_shares = ticker.shortableShares if _is_valid_number(ticker.shortableShares) else None

    # IB's own indicative stock-loan borrow cost (core/ib_borrow_rate.py, PROJECT_NOTES.md §6) -
    # a live-updating (hourly, every 15min 4-6pm ET) proxy for squeeze pressure: rising fee_rate
    # means rising demand to borrow/short the stock, unlike shares_short below which only updates
    # twice a month. A completely separate feed (public FTP) from everything else on this
    # connection - never blocks a row on its own failure.
    borrow_rate = await _get_borrow_rate(contract.symbol)

    float_stats = await _get_float_stats(contract.symbol)
    float_shares = float_stats["float_shares"]
    provider_short_percent = float_stats["short_percent"]
    shares_short = float_stats["shares_short"]
    short_interest_as_of = float_stats["short_interest_as_of"]
    float_as_of = datetime.fromtimestamp(float_stats["_fetched_at"], timezone.utc).isoformat()

    # Prefer the locally calculated shares_short/float_shares percentage (FRESH_START_DATA_AND_
    # SHORT_INTEREST_PLAN.md §2) over yfinance's own shortPercentOfFloat; fall back to the
    # provider value only when a raw shares_short figure isn't available for this symbol, and
    # flag the two if they disagree beyond tolerance rather than silently picking one.
    calculated_short_percent, _calc_reason = calculate_short_float_percent(shares_short, float_shares)
    days_to_cover, _dtc_reason = calculate_days_to_cover(shares_short, hist["avg_volume"])

    quality_flags = []
    if calculated_short_percent is not None:
        short_float_percent_value = calculated_short_percent
        discrepancy_flag = check_short_float_discrepancy(calculated_short_percent, provider_short_percent)
        if discrepancy_flag:
            quality_flags.append(discrepancy_flag)
    else:
        short_float_percent_value = provider_short_percent
        if short_float_percent_value is not None:
            quality_flags.append("short_float_percent_provider_supplied")
    if shares_short is None:
        quality_flags.append("shares_short_unavailable")
    if days_to_cover is None:
        quality_flags.append("days_to_cover_unavailable")
    if historical_data_missing:
        quality_flags.append("historical_bars_unavailable")
    elif today_volume is None or not hist["avg_volume"]:
        quality_flags.append("rel_volume_unavailable")
    if not historical_data_missing and hist["ttm_squeeze_on"] is None:
        quality_flags.append("ttm_squeeze_unavailable")  # fewer than 21 daily bars available yet
    if borrow_rate["fee_rate"] is None:
        quality_flags.append("ib_borrow_rate_unavailable")
    if shortable_shares is None:
        quality_flags.append("ib_shortable_shares_unavailable")

    return {
        "ticker": contract.symbol,
        "price": str(price),
        "float_shares": str(float_shares) if float_shares is not None else "N/A",
        "rel_volume": str(rel_volume),
        "change_percent": str(change_percent),
        "short_float_percent": str(short_float_percent_value) if short_float_percent_value is not None else "N/A",
        "shares_short": shares_short,
        "days_to_cover": days_to_cover,
        "short_interest_as_of": short_interest_as_of,
        # "yfinance" is honest about the actual relay; it is not a paid/licensed direct-exchange
        # feed, just the real dateShortInterest/sharesShort fields yfinance's .info exposes.
        "short_interest_source": "yfinance" if shares_short is not None else None,
        "float_source": "yfinance",
        "float_as_of": float_as_of,
        "ib_shortable_shares": int(shortable_shares) if shortable_shares is not None else None,
        "ib_shortable_shares_as_of": (
            datetime.now(timezone.utc).isoformat() if shortable_shares is not None else None
        ),
        "ttm_squeeze_on": hist["ttm_squeeze_on"],
        "ttm_squeeze_momentum": hist["ttm_squeeze_momentum"],
        "ib_borrow_fee_rate": borrow_rate["fee_rate"],
        "ib_borrow_rebate_rate": borrow_rate["rebate_rate"],
        "ib_borrow_rate_as_of": borrow_rate["as_of"],
        "quality_flags": quality_flags,
        "_price_num": price,
        "_change_num": change_percent,
        "_relvol_num": rel_volume,
        # Missing short-float data (yfinance lookup failed/rate-limited) defaults to 0, not
        # skipped - conservative "don't count it toward Prime if we don't actually know" rather
        # than accidentally treating an unknown as a pass.
        "_shortfloat_num": short_float_percent_value if short_float_percent_value is not None else 0.0,
        "_vol_w": hist["vol_w"],
        "_rsi": hist["rsi"],
    }


def _hist_rate_limit_allows(call_times, now):
    """True if a new reqHistoricalData call is allowed without exceeding IB's pacing limit, given
    call_times (a deque of past call epochs, mutated in place: entries older than the trailing
    window are dropped). Pure/sync, takes `now` explicitly rather than calling time.time() itself
    - testable with plain epoch floats, matching this codebase's existing TTL-testing convention
    (tests/test_schwab_api.py passes real epoch floats as fixture data, never mocks the clock).
    Bounded by construction: callers only append after this returns True, so call_times can never
    exceed _HIST_RATE_LIMIT_MAX_CALLS entries - no separate eviction/cap logic needed."""
    while call_times and now - call_times[0] >= _HIST_RATE_LIMIT_WINDOW_SECONDS:
        call_times.popleft()
    return len(call_times) < _HIST_RATE_LIMIT_MAX_CALLS


# Cached per HIST_CACHE_TTL_SECONDS above, gated by _hist_rate_limit_allows() to stay under IB's
# reqHistoricalData pacing limit regardless of how many symbols go stale at once.
async def _get_hist_stats(ib, contract):
    symbol = contract.symbol
    now = time.time()

    cached = _hist_cache.get(symbol)
    if cached and (now - cached[0]) < HIST_CACHE_TTL_SECONDS:
        return cached[1]

    if not _hist_rate_limit_allows(_hist_request_times, now):
        # Rate limit reached this window - serve the last cached value even if past its nominal
        # TTL, rather than degrading the whole row (RSI/vol/rel-volume too, not just TTM Squeeze -
        # see _hist_stats_or_degraded()). Deliberately different from the genuine-fetch-failure
        # path below (which still correctly returns None): a rate-limit skip is now an expected,
        # routine occurrence given the shorter TTL, not a real data-availability problem - treating
        # it like a fetch failure would cause needless degraded-row flapping every time budget runs out.
        return cached[1] if cached else None
    _hist_request_times.append(now)  # recorded on attempt, before the call - a failing/retried
    # request still consumed real IB pacing budget, so it must still count against ours.

    try:
        bars = await ib.reqHistoricalDataAsync(
            contract, endDateTime="", durationStr="30 D", barSizeSetting="1 day",
            whatToShow="TRADES", useRTH=True,
        )
    except Exception as e:
        print(f"⚠️ Historical data fetch failed for {symbol}: {e}")
        return None

    if len(bars) < 2:
        return None

    closes = [b.close for b in bars]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    volumes = [b.volume for b in bars]
    squeeze_on, squeeze_momentum = _compute_ttm_squeeze(highs, lows, closes)

    stats = {
        "rsi": _compute_rsi(closes),
        "vol_w": _compute_weekly_volatility(closes),
        "avg_volume": statistics.mean(volumes[:-1]) if len(volumes) > 1 else volumes[-1],
        "last_volume": volumes[-1],
        "last_close": closes[-1],
        "prev_close": closes[-2],
        "ttm_squeeze_on": squeeze_on,
        "ttm_squeeze_momentum": squeeze_momentum,
    }
    _hist_cache[symbol] = (now, stats)
    return stats
