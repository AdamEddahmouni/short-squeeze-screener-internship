import os
import sys
from unittest.mock import patch

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import chart_data


def _multiindex_frame(closes):
    index = pd.date_range("2026-07-10 09:30", periods=len(closes), freq="30min", tz="UTC")
    columns = pd.MultiIndex.from_product([["Close"], ["AAPL"]], names=["Price", "Ticker"])
    return pd.DataFrame({("Close", "AAPL"): closes}, index=index, columns=columns)


def test_fetch_chart_data_returns_points_from_multiindex_frame():
    frame = _multiindex_frame([100.0, 101.5, 99.25])
    with patch.object(chart_data.yf, "download", return_value=frame):
        points = chart_data.fetch_chart_data("AAPL")

    assert len(points) == 3
    assert points[0]["close"] == 100.0
    assert points[1]["close"] == 101.5
    assert "timestamp" in points[0]


def test_fetch_chart_data_drops_nan_rows():
    frame = _multiindex_frame([100.0, float("nan"), 99.25])
    with patch.object(chart_data.yf, "download", return_value=frame):
        points = chart_data.fetch_chart_data("AAPL")

    assert len(points) == 2
    assert [p["close"] for p in points] == [100.0, 99.25]


def test_fetch_chart_data_raises_on_empty_frame():
    with patch.object(chart_data.yf, "download", return_value=pd.DataFrame()):
        try:
            chart_data.fetch_chart_data("NOPE")
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_fetch_chart_data_raises_on_download_exception():
    with patch.object(chart_data.yf, "download", side_effect=RuntimeError("network down")):
        try:
            chart_data.fetch_chart_data("AAPL")
            assert False, "expected ValueError"
        except ValueError:
            pass


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
