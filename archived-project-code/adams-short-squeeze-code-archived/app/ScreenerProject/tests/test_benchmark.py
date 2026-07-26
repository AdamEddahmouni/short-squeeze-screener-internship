import os
import sys
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import benchmark


def _history_frame(rows):
    """rows: [(date, close), ...] -> a DataFrame shaped like yf.Ticker(...).history()'s output."""
    index = pd.to_datetime([d.isoformat() for d, _ in rows])
    return pd.DataFrame({"Close": [c for _, c in rows]}, index=index)


def test_fetch_benchmark_daily_closes_returns_date_keyed_dict():
    frame = _history_frame([(date(2026, 7, 10), 500.0), (date(2026, 7, 13), 505.0)])
    with patch.object(benchmark.yf, "Ticker", return_value=MagicMock(history=MagicMock(return_value=frame))):
        closes = benchmark.fetch_benchmark_daily_closes(date(2026, 7, 10))

    assert closes == {date(2026, 7, 10): 500.0, date(2026, 7, 13): 505.0}


def test_fetch_benchmark_daily_closes_returns_empty_dict_on_empty_frame():
    with patch.object(benchmark.yf, "Ticker", return_value=MagicMock(history=MagicMock(return_value=pd.DataFrame()))):
        assert benchmark.fetch_benchmark_daily_closes(date(2026, 7, 10)) == {}


def test_fetch_benchmark_daily_closes_returns_empty_dict_on_exception():
    with patch.object(benchmark.yf, "Ticker", side_effect=RuntimeError("network down")):
        assert benchmark.fetch_benchmark_daily_closes(date(2026, 7, 10)) == {}


def test_close_at_or_before_returns_latest_matching_date():
    closes = {date(2026, 7, 10): 500.0, date(2026, 7, 13): 505.0, date(2026, 7, 14): 510.0}
    assert benchmark.close_at_or_before(closes, date(2026, 7, 13)) == 505.0


def test_close_at_or_before_returns_none_when_dates_start_after():
    closes = {date(2026, 7, 14): 510.0}
    assert benchmark.close_at_or_before(closes, date(2026, 7, 10)) is None


def test_benchmark_pct_change_computes_percent_move_between_endpoints():
    closes = {date(2026, 7, 10): 500.0, date(2026, 7, 17): 550.0}
    pct = benchmark.benchmark_pct_change(closes, date(2026, 7, 10), date(2026, 7, 17))
    assert pct == 10.0


def test_benchmark_pct_change_returns_none_when_start_missing():
    closes = {date(2026, 7, 17): 550.0}
    assert benchmark.benchmark_pct_change(closes, date(2026, 7, 10), date(2026, 7, 17)) is None


def test_benchmark_pct_change_returns_none_when_start_price_is_zero():
    closes = {date(2026, 7, 10): 0.0, date(2026, 7, 17): 550.0}
    assert benchmark.benchmark_pct_change(closes, date(2026, 7, 10), date(2026, 7, 17)) is None


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except Exception as error:
            print(f"FAIL {test.__name__}: {error}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
