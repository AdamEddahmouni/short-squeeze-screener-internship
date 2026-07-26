import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.yfinance_float_api as yfinance_float_api


def _mock_ticker(info):
    ticker = MagicMock()
    ticker.info = info
    return ticker


def test_fetch_stats_extracts_expected_fields():
    info = {
        "floatShares": 15000000,
        "shortPercentOfFloat": 0.1667,
        "sharesShort": 2500000,
        "dateShortInterest": 1782777600,  # 2026-06-30 00:00:00 UTC
    }
    with patch.object(yfinance_float_api.yf, "Ticker", return_value=_mock_ticker(info)):
        stats = yfinance_float_api.fetch_float_and_short_interest_stats("PRIM")

    assert stats["float_shares"] == 15000000
    assert stats["short_percent"] == 16.67
    assert stats["shares_short"] == 2500000
    assert stats["short_interest_as_of"] == "2026-06-30"


def test_fetch_stats_handles_missing_fields():
    with patch.object(yfinance_float_api.yf, "Ticker", return_value=_mock_ticker({})):
        stats = yfinance_float_api.fetch_float_and_short_interest_stats("SUBP")

    assert stats == {
        "float_shares": None, "short_percent": None,
        "shares_short": None, "short_interest_as_of": None,
    }


def test_fetch_stats_handles_lookup_exception():
    with patch.object(yfinance_float_api.yf, "Ticker", side_effect=RuntimeError("boom")):
        stats = yfinance_float_api.fetch_float_and_short_interest_stats("FAIL")

    assert stats["float_shares"] is None
    assert stats["shares_short"] is None


def test_get_float_stats_caches_within_ttl():
    yfinance_float_api._float_cache.clear()
    info = {"floatShares": 5000000, "shortPercentOfFloat": 0.05, "sharesShort": 250000,
            "dateShortInterest": 1782777600}

    with patch.object(yfinance_float_api.yf, "Ticker", return_value=_mock_ticker(info)) as mock_ticker:
        first = yfinance_float_api.get_float_stats("CACHED")
        second = yfinance_float_api.get_float_stats("CACHED")

    assert first["float_shares"] == second["float_shares"] == 5000000
    assert mock_ticker.call_count == 1  # second call served from cache, no new lookup


def test_get_float_stats_async_shares_the_same_cache():
    yfinance_float_api._float_cache.clear()
    info = {"floatShares": 8000000, "shortPercentOfFloat": 0.08, "sharesShort": 640000,
            "dateShortInterest": 1782777600}

    with patch.object(yfinance_float_api.yf, "Ticker", return_value=_mock_ticker(info)) as mock_ticker:
        sync_stats = yfinance_float_api.get_float_stats("SHARED")
        async_stats = asyncio.run(yfinance_float_api.get_float_stats_async("SHARED"))

    assert sync_stats["float_shares"] == async_stats["float_shares"] == 8000000
    assert mock_ticker.call_count == 1  # async caller reused the sync caller's cache entry


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0

    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
