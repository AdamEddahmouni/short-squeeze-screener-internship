import asyncio
import sys
import os
import time
from collections import deque
from types import SimpleNamespace
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.ib_api as ib_api


def test_enrichment_target_is_fifteen_seconds():
    assert ib_api.ENRICH_INTERVAL_SECONDS == 15


def test_env_int_reads_valid_integer():
    with patch.dict(os.environ, {"TEST_IB_INTEGER": "123"}):
        assert ib_api._env_int("TEST_IB_INTEGER", 7) == 123


def test_env_int_falls_back_for_blank_or_invalid_value():
    with patch.dict(os.environ, {"TEST_IB_INTEGER": ""}):
        assert ib_api._env_int("TEST_IB_INTEGER", 7) == 7
    with patch.dict(os.environ, {"TEST_IB_INTEGER": "invalid"}):
        assert ib_api._env_int("TEST_IB_INTEGER", 7) == 7


def test_rsi_neutral_default_on_insufficient_data():
    assert ib_api._compute_rsi([1, 2, 3]) == 50.0


def test_rsi_all_gains_is_100():
    closes = [10 + i for i in range(15)]  # steadily rising, no losses
    assert ib_api._compute_rsi(closes) == 100.0


def test_rsi_hand_computed_example():
    # 15 closes -> 14 deltas, split evenly gain/loss for an easy hand-check
    closes = [100, 101, 102, 103, 104, 105, 106, 107,
              106, 105, 104, 103, 102, 101, 100]
    rsi = ib_api._compute_rsi(closes)
    assert 0 <= rsi <= 100


def test_weekly_volatility_zero_on_flat_prices():
    closes = [100, 100, 100, 100, 100, 100]
    assert ib_api._compute_weekly_volatility(closes) == 0.0


def test_weekly_volatility_insufficient_data_returns_zero():
    assert ib_api._compute_weekly_volatility([100, 101]) == 0.0


# --- _hist_rate_limit_allows() (2026-07-17) - keeps reqHistoricalData calls under IB's pacing
# limit now that HIST_CACHE_TTL_SECONDS is short enough to hit it routinely, not just on cold
# start. Pure/sync, plain epoch floats as data - no clock mocking, matching this codebase's
# established TTL-testing convention (see tests/test_schwab_api.py). ---

def test_hist_rate_limit_allows_when_under_budget():
    call_times = deque([1000.0] * (ib_api._HIST_RATE_LIMIT_MAX_CALLS - 1))
    assert ib_api._hist_rate_limit_allows(call_times, now=1001.0) is True


def test_hist_rate_limit_denies_at_budget():
    call_times = deque([1000.0] * ib_api._HIST_RATE_LIMIT_MAX_CALLS)
    assert ib_api._hist_rate_limit_allows(call_times, now=1001.0) is False


def test_hist_rate_limit_allows_again_once_oldest_call_ages_out_of_window():
    call_times = deque([1000.0] * ib_api._HIST_RATE_LIMIT_MAX_CALLS)
    now = 1000.0 + ib_api._HIST_RATE_LIMIT_WINDOW_SECONDS
    assert ib_api._hist_rate_limit_allows(call_times, now=now) is True
    assert len(call_times) == 0  # the whole stale batch was pruned, not just one entry


def test_hist_rate_limit_prunes_only_entries_past_the_window():
    call_times = deque([1000.0, 1000.0, 1500.0])
    now = 1000.0 + ib_api._HIST_RATE_LIMIT_WINDOW_SECONDS
    ib_api._hist_rate_limit_allows(call_times, now=now)
    assert list(call_times) == [1500.0]


def test_is_ib_available_reflects_connection_flag():
    with ib_api._state_lock:
        ib_api._connected = True
    assert ib_api.is_ib_available() is True

    with ib_api._state_lock:
        ib_api._connected = False
    assert ib_api.is_ib_available() is False


def _fabricated_snapshot():
    # Ticker names/comments below predate the 2026-07-17 redesign (score_setup()-based
    # Prime/Subprime scoring used to happen inside rank_and_group_stocks_ib() itself); kept as
    # descriptive sample data - a rich row, a partial row, and a sparse row - since tier
    # classification now happens cross-provider in controller.py, not here.
    return [
        {  # rich row: every field populated
            "ticker": "PRIM", "price": "5.00", "float_shares": "5000000",
            "rel_volume": "6.0", "change_percent": "15.0",
            "short_float_percent": "10.0",
            "shares_short": 500000, "days_to_cover": 2.5,
            "short_interest_as_of": "2026-06-30", "short_interest_source": "yfinance",
            "float_as_of": "2026-07-13T12:00:00+00:00", "float_source": "yfinance",
            "ib_shortable_shares": 1000, "ib_shortable_shares_as_of": "2026-07-13T12:00:15+00:00",
            "quality_flags": [],
            "_price_num": 5.0, "_change_num": 15.0, "_relvol_num": 6.0, "_shortfloat_num": 10.0,
            "_vol_w": 10.0, "_rsi": 40.0,
        },
        {  # partial row: no independently reported short-interest figures
            "ticker": "SUBP", "price": "8.00", "float_shares": "5000000",
            "rel_volume": "2.0", "change_percent": "12.0",
            "short_float_percent": "8.0",
            "shares_short": None, "days_to_cover": None,
            "short_interest_as_of": None, "short_interest_source": None,
            "float_as_of": "2026-07-13T12:00:00+00:00", "float_source": "yfinance",
            "ib_shortable_shares": 500, "ib_shortable_shares_as_of": "2026-07-13T12:00:15+00:00",
            "quality_flags": ["short_float_percent_provider_supplied", "shares_short_unavailable",
                               "days_to_cover_unavailable"],
            "_price_num": 8.0, "_change_num": 12.0, "_relvol_num": 2.0, "_shortfloat_num": 8.0,
            "_vol_w": 5.0, "_rsi": 55.0,
        },
        {  # sparse row: high price, low volume/short-float, no short-interest figures
            "ticker": "FAIL", "price": "50.00", "float_shares": "5000000",
            "rel_volume": "1.0", "change_percent": "1.0",
            "short_float_percent": "1.0",
            "shares_short": None, "days_to_cover": None,
            "short_interest_as_of": None, "short_interest_source": None,
            "float_as_of": "2026-07-13T12:00:00+00:00", "float_source": "yfinance",
            "ib_shortable_shares": 0, "ib_shortable_shares_as_of": "2026-07-13T12:00:15+00:00",
            "quality_flags": ["short_float_percent_provider_supplied", "shares_short_unavailable",
                               "days_to_cover_unavailable"],
            "_price_num": 50.0, "_change_num": 1.0, "_relvol_num": 1.0, "_shortfloat_num": 1.0,
            "_vol_w": 0.0, "_rsi": 50.0,
        },
    ]


# 2026-07-17 redesign (SQUEEZE_FORMULA_REDESIGN_HANDOFF.md): rank_and_group_stocks_ib() no
# longer scores/splits with core/scoring.py::score_setup() - it returns every candidate as a
# flat list, and controller.py classifies Prime/Subprime off the composite squeeze score
# (core/squeeze_score.py::classify_tier()) once corroboration/TTM Squeeze are available
# cross-provider. See tests/test_controller_snapshot.py for tier-classification coverage.
def test_rank_and_group_stocks_ib_returns_flat_candidate_list():
    with ib_api._state_lock:
        ib_api._latest_snapshot.clear()
        ib_api._latest_snapshot.extend(_fabricated_snapshot())

    candidates = ib_api.rank_and_group_stocks_ib()

    assert [s["Ticker"] for s in candidates] == ["PRIM", "SUBP", "FAIL"]


def test_rank_and_group_stocks_ib_shape_matches_filters_module():
    from core.filters import rank_and_group_stocks  # noqa: F401 (shape reference only)

    with ib_api._state_lock:
        ib_api._latest_snapshot.clear()
        ib_api._latest_snapshot.extend(_fabricated_snapshot())

    candidates = ib_api.rank_and_group_stocks_ib()
    expected_keys = {"Ticker", "Price", "Float", "RelVolume", "ChangePercent",
                      "ShortFloat", "Target", "StopLoss", "Headline",
                      "SharesShort", "DaysToCover", "ShortInterestAsOf", "ShortInterestSource",
                      "FloatAsOf", "FloatSource", "IbShortableShares", "IbShortableSharesAsOf",
                      "SchwabHtbQuantity", "SchwabHtbRate", "SchwabIsHardToBorrow",
                      "SchwabHtbAsOf", "TtmSqueezeOn", "TtmSqueezeMomentum",
                      "IbBorrowFeeRate", "IbBorrowRebateRate", "IbBorrowRateAsOf", "QualityFlags"}
    assert set(candidates[0].keys()) == expected_keys


def test_rank_and_group_stocks_ib_carries_short_interest_provenance():
    with ib_api._state_lock:
        ib_api._latest_snapshot.clear()
        ib_api._latest_snapshot.extend(_fabricated_snapshot())

    candidates = ib_api.rank_and_group_stocks_ib()
    prim, subp = candidates[0], candidates[1]

    assert prim["SharesShort"] == 500000
    assert prim["DaysToCover"] == 2.5
    assert prim["ShortInterestSource"] == "yfinance"
    assert prim["QualityFlags"] == []

    # SUBP has no independently reported shares_short - must not be silently defaulted to 0
    # or fabricated, and must carry the reason flags forward instead.
    assert subp["SharesShort"] is None
    assert subp["DaysToCover"] is None
    assert "shares_short_unavailable" in subp["QualityFlags"]


def test_get_filtered_stocks_ib_shape():
    with ib_api._state_lock:
        ib_api._latest_snapshot.clear()
        ib_api._latest_snapshot.extend(_fabricated_snapshot())

    stocks = ib_api.get_filtered_stocks_ib()
    expected_keys = {"Ticker", "Price", "Float", "RelVolume", "ChangePercent", "Headline"}
    assert set(stocks[0].keys()) == expected_keys
    assert len(stocks) == 3  # unfiltered - get_filtered_stocks_ib() mirrors the raw snapshot


def test_rank_and_group_stocks_ib_empty_when_no_snapshot():
    with ib_api._state_lock:
        ib_api._latest_snapshot.clear()

    candidates = ib_api.rank_and_group_stocks_ib()
    assert candidates == []


# --- defect fix: connected-but-broken enrichment must not block the Schwab/Finviz fallback ---

def _reset_enrichment_health():
    with ib_api._state_lock:
        ib_api._connected = True
        ib_api._consecutive_enrichment_failures = 0


def test_is_ib_available_false_when_enrichment_failures_exceed_threshold():
    _reset_enrichment_health()
    for _ in range(ib_api.MAX_CONSECUTIVE_ENRICHMENT_FAILURES):
        ib_api._record_enrichment_result(0)
    assert ib_api.is_ib_available() is False
    _reset_enrichment_health()


def test_is_ib_available_true_below_failure_threshold():
    _reset_enrichment_health()
    for _ in range(ib_api.MAX_CONSECUTIVE_ENRICHMENT_FAILURES - 1):
        ib_api._record_enrichment_result(0)
    assert ib_api.is_ib_available() is True
    _reset_enrichment_health()


def test_record_enrichment_result_resets_counter_on_success():
    _reset_enrichment_health()
    ib_api._record_enrichment_result(0)
    ib_api._record_enrichment_result(0)
    ib_api._record_enrichment_result(5)  # a healthy pass resets it
    assert ib_api.is_ib_available() is True
    _reset_enrichment_health()


def test_record_enrichment_exception_counts_toward_threshold():
    _reset_enrichment_health()
    for _ in range(ib_api.MAX_CONSECUTIVE_ENRICHMENT_FAILURES):
        ib_api._record_enrichment_exception()
    assert ib_api.is_ib_available() is False
    _reset_enrichment_health()


def test_reset_enrichment_failures_clears_counter():
    _reset_enrichment_health()
    for _ in range(ib_api.MAX_CONSECUTIVE_ENRICHMENT_FAILURES):
        ib_api._record_enrichment_exception()
    ib_api._reset_enrichment_failures()
    assert ib_api.is_ib_available() is True
    _reset_enrichment_health()


# --- _get_hist_stats() rate-limit gating (2026-07-17) - untested at this async-execution level
# before now (always mocked out as a _build_row() dependency elsewhere in this file); this is a
# real behavior change so it needs direct coverage. Reset module state around each test, mirroring
# the schwab_api._hist_cache.clear() precedent in tests/test_schwab_api.py. ---

class _FakeIB:
    def __init__(self, bars=None, exc=None):
        self._bars, self._exc = bars, exc
        self.call_count = 0

    async def reqHistoricalDataAsync(self, *args, **kwargs):
        self.call_count += 1
        if self._exc:
            raise self._exc
        return self._bars


def _bar(close, high, low, volume):
    return SimpleNamespace(close=close, high=high, low=low, volume=volume)


def _reset_hist_state():
    ib_api._hist_cache.clear()
    ib_api._hist_request_times.clear()


def test_get_hist_stats_cache_hit_never_calls_ib():
    _reset_hist_state()
    contract = SimpleNamespace(symbol="CACHED")
    ib_api._hist_cache["CACHED"] = (time.time(), {"rsi": 55.0})
    fake_ib = _FakeIB(exc=AssertionError("should not be called on a cache hit"))

    stats = asyncio.run(ib_api._get_hist_stats(fake_ib, contract))

    assert stats == {"rsi": 55.0}
    assert fake_ib.call_count == 0
    _reset_hist_state()


def test_get_hist_stats_successful_fetch_records_request_time_and_caches():
    _reset_hist_state()
    contract = SimpleNamespace(symbol="FRESH")
    bars = [_bar(10 + i, 10 + i, 10 + i, 1000) for i in range(25)]
    fake_ib = _FakeIB(bars=bars)

    stats = asyncio.run(ib_api._get_hist_stats(fake_ib, contract))

    assert stats is not None
    assert fake_ib.call_count == 1
    assert len(ib_api._hist_request_times) == 1
    assert "FRESH" in ib_api._hist_cache
    _reset_hist_state()


def test_get_hist_stats_returns_stale_cache_when_budget_saturated():
    _reset_hist_state()
    contract = SimpleNamespace(symbol="STALE")
    stale_stats = {"rsi": 42.0}
    ib_api._hist_cache["STALE"] = (time.time() - ib_api.HIST_CACHE_TTL_SECONDS - 1, stale_stats)
    ib_api._hist_request_times.extend([time.time()] * ib_api._HIST_RATE_LIMIT_MAX_CALLS)
    fake_ib = _FakeIB(exc=AssertionError("should not be called while budget is saturated"))

    stats = asyncio.run(ib_api._get_hist_stats(fake_ib, contract))

    assert stats == stale_stats
    assert fake_ib.call_count == 0
    _reset_hist_state()


def test_get_hist_stats_returns_none_when_budget_saturated_and_no_cache():
    _reset_hist_state()
    contract = SimpleNamespace(symbol="NEVERFETCHED")
    ib_api._hist_request_times.extend([time.time()] * ib_api._HIST_RATE_LIMIT_MAX_CALLS)
    fake_ib = _FakeIB(exc=AssertionError("should not be called while budget is saturated"))

    stats = asyncio.run(ib_api._get_hist_stats(fake_ib, contract))

    assert stats is None
    assert fake_ib.call_count == 0
    _reset_hist_state()


# --- defect fix: historical-data failure must not discard a row that has a usable live price ---

def test_hist_stats_or_degraded_passes_through_real_stats():
    real_stats = {"vol_w": 5.0, "rsi": 60.0, "avg_volume": 100, "last_volume": 200,
                  "last_close": 10.0, "prev_close": 9.5}
    stats, degraded = ib_api._hist_stats_or_degraded(real_stats)
    assert stats == real_stats
    assert degraded is False


def test_hist_stats_or_degraded_returns_safe_placeholder_when_none():
    stats, degraded = ib_api._hist_stats_or_degraded(None)
    assert degraded is True
    assert stats["rsi"] == 50.0
    assert stats["vol_w"] == 0.0
    assert stats["avg_volume"] is None
    assert stats["last_close"] is None


_NO_BORROW_RATE = {"fee_rate": None, "rebate_rate": None, "available": None, "as_of": None}


async def _fake_borrow_rate(_symbol):
    return _NO_BORROW_RATE


def test_build_row_keeps_row_when_historical_data_fails_but_live_price_exists():
    contract = SimpleNamespace(symbol="PRIM")
    ticker = SimpleNamespace(last=5.0, close=4.35, shortableShares=1000)
    float_stats = {"float_shares": 5_000_000, "short_percent": 10.0, "shares_short": 500_000,
                   "short_interest_as_of": "2026-06-30", "_fetched_at": 0}

    async def run():
        with patch.object(ib_api, "_get_hist_stats", return_value=None), \
             patch.object(ib_api, "_get_float_stats", return_value=float_stats), \
             patch.object(ib_api, "_get_borrow_rate", _fake_borrow_rate):
            return await ib_api._build_row(None, contract, ticker)

    row = asyncio.run(run())

    assert row is not None  # previously discarded entirely once reqHistoricalData failed
    assert row["ticker"] == "PRIM"
    assert row["price"] == "5.0"
    assert "historical_bars_unavailable" in row["quality_flags"]
    assert row["_relvol_num"] == 0.0  # can't be computed without historical average volume
    assert row["_vol_w"] == 0.0
    assert row["_rsi"] == 50.0


def test_build_row_returns_none_when_no_price_source_at_all():
    contract = SimpleNamespace(symbol="FAIL")
    ticker = SimpleNamespace(last=float("nan"), close=float("nan"), shortableShares=0)
    float_stats = {"float_shares": None, "short_percent": None, "shares_short": None,
                   "short_interest_as_of": None, "_fetched_at": 0}

    async def run():
        with patch.object(ib_api, "_get_hist_stats", return_value=None), \
             patch.object(ib_api, "fetch_finnhub_price", return_value=None), \
             patch.object(ib_api, "_get_float_stats", return_value=float_stats), \
             patch.object(ib_api, "_get_borrow_rate", _fake_borrow_rate):
            return await ib_api._build_row(None, contract, ticker)

    assert asyncio.run(run()) is None


def test_build_row_carries_ib_borrow_rate_fields():
    contract = SimpleNamespace(symbol="STAK")
    ticker = SimpleNamespace(last=5.0, close=4.35, shortableShares=1000)
    float_stats = {"float_shares": 5_000_000, "short_percent": 10.0, "shares_short": 500_000,
                   "short_interest_as_of": "2026-06-30", "_fetched_at": 0}
    borrow_rate = {"fee_rate": 5.0, "rebate_rate": -4.5, "available": 1200,
                    "as_of": "2026-07-16T20:00:00+00:00"}

    async def fake_borrow_rate(_symbol):
        return borrow_rate

    async def run():
        with patch.object(ib_api, "_get_hist_stats", return_value=None), \
             patch.object(ib_api, "_get_float_stats", return_value=float_stats), \
             patch.object(ib_api, "_get_borrow_rate", fake_borrow_rate):
            return await ib_api._build_row(None, contract, ticker)

    row = asyncio.run(run())
    assert row["ib_borrow_fee_rate"] == 5.0
    assert row["ib_borrow_rebate_rate"] == -4.5
    assert row["ib_borrow_rate_as_of"] == "2026-07-16T20:00:00+00:00"
    assert "ib_borrow_rate_unavailable" not in row["quality_flags"]


def test_build_row_flags_ib_borrow_rate_unavailable_when_feed_has_no_data():
    contract = SimpleNamespace(symbol="UNKNOWN")
    ticker = SimpleNamespace(last=5.0, close=4.35, shortableShares=1000)
    float_stats = {"float_shares": 5_000_000, "short_percent": 10.0, "shares_short": 500_000,
                   "short_interest_as_of": "2026-06-30", "_fetched_at": 0}

    async def run():
        with patch.object(ib_api, "_get_hist_stats", return_value=None), \
             patch.object(ib_api, "_get_float_stats", return_value=float_stats), \
             patch.object(ib_api, "_get_borrow_rate", _fake_borrow_rate):
            return await ib_api._build_row(None, contract, ticker)

    row = asyncio.run(run())
    assert row["ib_borrow_fee_rate"] is None
    assert "ib_borrow_rate_unavailable" in row["quality_flags"]


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
