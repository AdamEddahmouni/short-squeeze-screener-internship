import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.yfinance_news_api as yfinance_news_api


def _raw_item(title, summary=""):
    return {"content": {"title": title, "summary": summary, "pubDate": "2026-07-13T00:00:00Z",
                         "canonicalUrl": {"url": "https://example.com"}}}


def _mock_ticker(items):
    ticker = MagicMock()
    ticker.news = items
    return ticker


# Regression tests for a real bug caught during live testing (2026-07-13): yfinance's
# unofficial .news endpoint returns Yahoo's general "trending on this ticker's page" carousel,
# not strictly relevant single-company news - unrelated headlines (e.g. Opendoor/OPEN news,
# generic market roundups) were being tagged and used as if they were the queried ticker's own
# news, which would silently compute sentiment from irrelevant text.

def test_filters_out_headline_that_does_not_mention_the_ticker():
    items = [_raw_item("Why Is Opendoor (OPEN) Stock Rocketing Higher Today")]
    with patch.object(yfinance_news_api.yf, "Ticker", return_value=_mock_ticker(items)):
        news = yfinance_news_api.fetch_yfinance_news(["SRXH"])
    assert news == []


def test_filters_out_generic_market_roundup_headline():
    items = [_raw_item("BC-Most Active Stocks")]
    with patch.object(yfinance_news_api.yf, "Ticker", return_value=_mock_ticker(items)):
        news = yfinance_news_api.fetch_yfinance_news(["MIMI"])
    assert news == []


def test_keeps_headline_that_mentions_the_ticker_in_title():
    items = [_raw_item("Sky Quarry (SKYQ) Soars 20.8% on Foreland Refinery Update")]
    with patch.object(yfinance_news_api.yf, "Ticker", return_value=_mock_ticker(items)):
        news = yfinance_news_api.fetch_yfinance_news(["SKYQ"])
    assert len(news) == 1
    assert news[0]["tickers"] == ["SKYQ"]


def test_keeps_headline_that_mentions_the_ticker_only_in_summary():
    items = [_raw_item("Company announces quarterly results", summary="GME reported record revenue.")]
    with patch.object(yfinance_news_api.yf, "Ticker", return_value=_mock_ticker(items)):
        news = yfinance_news_api.fetch_yfinance_news(["GME"])
    assert len(news) == 1


def test_ticker_match_is_whole_word_not_substring():
    # "AMEN" contains "AME" as a substring but must not match ticker "AME" as a whole word.
    items = [_raw_item("AMEN Corp announces new product line")]
    with patch.object(yfinance_news_api.yf, "Ticker", return_value=_mock_ticker(items)):
        news = yfinance_news_api.fetch_yfinance_news(["AME"])
    assert news == []


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
