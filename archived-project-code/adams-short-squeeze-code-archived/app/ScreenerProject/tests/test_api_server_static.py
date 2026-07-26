import asyncio
import os
import sys
import tempfile
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx

import api_server
from core import snapshot_store


def _get(path):
    async def request():
        transport = httpx.ASGITransport(app=api_server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)
    return asyncio.run(request())


# --- web UI (2026-07-16): / and /static/* are a pure read-only viewer layered on top of the
# existing /health + /screener routes - these tests lock down that the routes actually serve the
# real committed static/ files and that adding them didn't disturb the pre-existing contract.

def test_index_route_serves_html():
    response = _get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>Short Squeeze Screener</title>" in response.text


def test_static_css_is_served():
    response = _get("/static/style.css")
    assert response.status_code == 200
    assert "css" in response.headers["content-type"]


def test_static_js_is_served():
    response = _get("/static/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]


def test_static_missing_file_is_404():
    response = _get("/static/does-not-exist.js")
    assert response.status_code == 404


# --- cache-busting (2026-07-17): / and /static/* must force revalidation on every load, not get
# silently served stale from a browser's own cache - observed live, a fixed app.js kept rendering
# old behavior in a real browser despite the server confirmed serving the fix.

def test_index_route_is_not_cached():
    response = _get("/")
    assert response.headers.get("cache-control") == "no-cache"


def test_static_file_is_not_cached():
    response = _get("/static/app.js")
    assert response.headers.get("cache-control") == "no-cache"


def test_health_route_is_unaffected_by_cache_header():
    response = _get("/health")
    assert response.headers.get("cache-control") != "no-cache"


# --- /news (2026-07-16): same read-only file-backed pattern as /screener, second snapshot ---

def test_news_returns_empty_list_before_first_write():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "news_snapshot.json")
        with patch.object(api_server, "NEWS_SNAPSHOT_PATH", path):
            response = _get("/news")
    assert response.status_code == 200
    assert response.json() == []


def test_news_serves_written_headlines():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "news_snapshot.json")
        headlines = [{"headline": "Big move today", "confidence_score": 0.81,
                      "tickers": ["GME"], "url": "https://example.com/a"}]
        snapshot_store.write_snapshot(headlines, path)
        with patch.object(api_server, "NEWS_SNAPSHOT_PATH", path):
            response = _get("/news")
    assert response.status_code == 200
    assert response.json() == headlines


def test_news_rejects_malformed_snapshot():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "news_snapshot.json")
        with open(path, "w", encoding="utf-8") as file:
            file.write("not json")
        with patch.object(api_server, "NEWS_SNAPSHOT_PATH", path):
            response = _get("/news")
    assert response.status_code == 503


# --- /chart/{ticker} (2026-07-16): on-demand yfinance series, web equivalent of the Tkinter
# Chart tab - route just delegates to core/chart_data.py, so these tests mock that boundary
# rather than yfinance itself (yfinance's own behavior is covered by test_chart_data.py).

def test_chart_returns_points_for_valid_ticker():
    points = [{"timestamp": "2026-07-10T09:30:00-04:00", "close": 100.0}]
    with patch.object(api_server.chart_data, "fetch_chart_data", return_value=points):
        response = _get("/chart/AAPL")
    assert response.status_code == 200
    assert response.json() == points


def test_chart_returns_404_for_invalid_ticker():
    with patch.object(api_server.chart_data, "fetch_chart_data", side_effect=ValueError("no data")):
        response = _get("/chart/NOPE")
    assert response.status_code == 404


# --- /squeeze-score-history/{ticker} (2026-07-16): route just delegates to
# core/squeeze_score_history.py, mocked at that boundary (its own file-parsing behavior is
# covered by test_squeeze_score_history.py).

def test_squeeze_score_history_returns_points():
    points = [{"timestamp": "2026-07-16T00:00:00+00:00", "squeeze_score": 72.5}]
    with patch.object(api_server.squeeze_score_history, "read_score_history", return_value=points):
        response = _get("/squeeze-score-history/GME")
    assert response.status_code == 200
    assert response.json() == points


def test_squeeze_score_history_returns_empty_list_when_none_logged():
    with patch.object(api_server.squeeze_score_history, "read_score_history", return_value=[]):
        response = _get("/squeeze-score-history/NOPE")
    assert response.status_code == 200
    assert response.json() == []


# --- /squeeze-score-track-record (2026-07-16): route just delegates to
# core/squeeze_score_track_record.py, mocked at that boundary (band math itself is covered by
# test_squeeze_score_track_record.py).

def test_squeeze_score_track_record_returns_summary():
    summary = [{"score_band": "90+", "n": 2, "avg_change_percent": 5.0, "hit_rate_percent": 100.0}]
    with patch.object(api_server.squeeze_score_track_record, "summarize_outcomes", return_value=summary):
        response = _get("/squeeze-score-track-record")
    assert response.status_code == 200
    assert response.json() == summary


def test_squeeze_score_track_record_returns_empty_list_when_nothing_graded():
    with patch.object(api_server.squeeze_score_track_record, "summarize_outcomes", return_value=[]):
        response = _get("/squeeze-score-track-record")
    assert response.status_code == 200
    assert response.json() == []


# --- /corroboration-track-record (2026-07-17): route just delegates to
# core/corroboration_track_record.py, mocked at that boundary (band math itself is covered by
# test_corroboration_track_record.py).

def test_corroboration_track_record_returns_summary():
    summary = [{"score_band": "4", "n": 2, "avg_change_percent": 5.0, "hit_rate_percent": 100.0}]
    with patch.object(api_server.corroboration_track_record, "summarize_outcomes", return_value=summary):
        response = _get("/corroboration-track-record")
    assert response.status_code == 200
    assert response.json() == summary


def test_corroboration_track_record_returns_empty_list_when_nothing_graded():
    with patch.object(api_server.corroboration_track_record, "summarize_outcomes", return_value=[]):
        response = _get("/corroboration-track-record")
    assert response.status_code == 200
    assert response.json() == []


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
