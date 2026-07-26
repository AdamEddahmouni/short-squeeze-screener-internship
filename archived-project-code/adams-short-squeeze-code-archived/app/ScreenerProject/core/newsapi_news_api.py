import os
import time
import requests
from dotenv import load_dotenv

# Loaded here (not just in main.py) so NEWSAPI_KEY is populated regardless of entry point -
# the app, a standalone test script, or a REPL import all go through this module. Path is
# anchored to this file's location, not cwd, since callers run from different working
# directories. No-ops quietly if app/ScreenerProject/.env doesn't exist (see .env.example).
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Last-resort fallback: only called when yfinance's unofficial `.news` endpoint (the
# primary free source, PROJECT_NOTES.md §8a) returns nothing for a refresh cycle. NewsAPI's
# free tier is officially documented but capped at ~100 requests/day and ~24h-delayed, so it's
# not fit to be a primary source - MAX_REQUESTS_PER_DAY stays well under the real cap, and the
# cache TTL is long since re-fetching faster than the tier's own delay buys nothing.
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")

MAX_REQUESTS_PER_DAY = 90
_request_count = 0
_window_start = time.time()

_news_cache = {}


def _reset_window_if_expired():
    global _request_count, _window_start
    now = time.time()
    if now - _window_start >= 86400:
        _request_count = 0
        _window_start = now


def _quota_available():
    _reset_window_if_expired()
    return _request_count < MAX_REQUESTS_PER_DAY


def _fetch_single_ticker_news(ticker):
    global _request_count
    if not _quota_available():
        print(f"⚠️ NewsAPI daily quota ({MAX_REQUESTS_PER_DAY}) reached; skipping {ticker}.")
        return []

    url = (
        f"https://newsapi.org/v2/everything?q={ticker}"
        f"&pageSize=10&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}"
    )
    try:
        response = requests.get(url, timeout=10)
        _request_count += 1
        response.raise_for_status()
        articles = response.json().get("articles", [])
    except Exception as e:
        print(f"⚠️ Error fetching NewsAPI news for {ticker}: {e}")
        return []

    headlines = []
    for article in articles:
        title = article.get("title")
        if not title:
            continue
        headlines.append({
            "headline": title,
            "timestamp": article.get("publishedAt", "Unknown time"),
            "url": article.get("url", ""),
            "tickers": [ticker]
        })
    return headlines


# Fetches recent news for a list of tickers via NewsAPI.org, returning the same shape as
# finviz_api.fetch_all_finviz_api_news()/yfinance_news_api.fetch_yfinance_news() so it's a
# drop-in third-tier fallback for controller.py. No-ops (returns []) if NEWSAPI_KEY isn't set.
def fetch_newsapi_news(tickers, cache_ttl_seconds=1800):
    if not NEWSAPI_KEY:
        return []

    all_headlines = []
    now = time.time()

    for ticker in tickers:
        cached = _news_cache.get(ticker)
        if cached and (now - cached[0]) < cache_ttl_seconds:
            all_headlines.extend(cached[1])
            continue

        headlines = _fetch_single_ticker_news(ticker)
        _news_cache[ticker] = (now, headlines)
        all_headlines.extend(headlines)

    return all_headlines
