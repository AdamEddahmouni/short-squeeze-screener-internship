import asyncio
import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.ib_borrow_rate as ib_borrow_rate


_SAMPLE_FEED = (
    "20260716 20:00:00\r\n"
    "#SYM|CUR|NAME|CONTRACT|ISIN|REBATERATE|FEERATE|AVAILABLE\r\n"
    "AAPL|USD|Apple Inc|265598|US0378331005|-0.25|0.30|5000000\r\n"
    "STAK|USD|Some Squeeze Co|999999|US0000000000|-4.5|5.0|1200\r\n"
    "BADROW|USD|Not enough fields\r\n"
    "#EOF\r\n"
    "\r\n"
)


def _reset_cache():
    with ib_borrow_rate._cache_lock:
        ib_borrow_rate._cached_at = 0.0
        ib_borrow_rate._rates_by_symbol = {}
        ib_borrow_rate._last_fetch_error = None


def test_parse_hand_computed_example():
    rates = ib_borrow_rate._parse(_SAMPLE_FEED)
    assert rates["AAPL"] == {"fee_rate": 0.30, "rebate_rate": -0.25, "available": 5000000}
    assert rates["STAK"] == {"fee_rate": 5.0, "rebate_rate": -4.5, "available": 1200}


def test_parse_skips_malformed_row_without_raising():
    rates = ib_borrow_rate._parse(_SAMPLE_FEED)
    assert "BADROW" not in rates
    assert len(rates) == 2  # only the two well-formed data rows


def test_parse_empty_feed_returns_empty_dict():
    assert ib_borrow_rate._parse("") == {}


def test_get_borrow_rate_returns_data_for_known_symbol():
    _reset_cache()
    with patch.object(ib_borrow_rate, "_fetch_raw", return_value=_SAMPLE_FEED) as mock_fetch:
        result = ib_borrow_rate.get_borrow_rate("STAK")
    assert result["fee_rate"] == 5.0
    assert result["rebate_rate"] == -4.5
    assert result["available"] == 1200
    assert result["as_of"] is not None
    mock_fetch.assert_called_once()


def test_get_borrow_rate_returns_all_none_for_symbol_not_in_feed():
    _reset_cache()
    with patch.object(ib_borrow_rate, "_fetch_raw", return_value=_SAMPLE_FEED):
        result = ib_borrow_rate.get_borrow_rate("NOTREAL")
    assert result == {"fee_rate": None, "rebate_rate": None, "available": None, "as_of": None}


def test_get_borrow_rate_survives_fetch_failure_without_raising():
    _reset_cache()
    with patch.object(ib_borrow_rate, "_fetch_raw", side_effect=OSError("connection timed out")):
        result = ib_borrow_rate.get_borrow_rate("AAPL")
    assert result == {"fee_rate": None, "rebate_rate": None, "available": None, "as_of": None}


def test_get_borrow_rate_caches_within_ttl_one_fetch_for_many_lookups():
    _reset_cache()
    with patch.object(ib_borrow_rate, "_fetch_raw", return_value=_SAMPLE_FEED) as mock_fetch:
        ib_borrow_rate.get_borrow_rate("AAPL")
        ib_borrow_rate.get_borrow_rate("STAK")
        ib_borrow_rate.get_borrow_rate("NOTREAL")
    mock_fetch.assert_called_once()  # one feed download serves every symbol lookup this cycle


def test_get_borrow_rate_refetches_after_ttl_expires():
    _reset_cache()
    with patch.object(ib_borrow_rate, "_fetch_raw", return_value=_SAMPLE_FEED) as mock_fetch:
        ib_borrow_rate.get_borrow_rate("AAPL")
        with ib_borrow_rate._cache_lock:
            ib_borrow_rate._cached_at -= ib_borrow_rate.CACHE_TTL_SECONDS + 1  # force staleness
        ib_borrow_rate.get_borrow_rate("AAPL")
    assert mock_fetch.call_count == 2


def test_get_borrow_rate_async_wraps_sync_lookup():
    _reset_cache()
    with patch.object(ib_borrow_rate, "_fetch_raw", return_value=_SAMPLE_FEED):
        result = asyncio.run(ib_borrow_rate.get_borrow_rate_async("STAK"))
    assert result["fee_rate"] == 5.0
