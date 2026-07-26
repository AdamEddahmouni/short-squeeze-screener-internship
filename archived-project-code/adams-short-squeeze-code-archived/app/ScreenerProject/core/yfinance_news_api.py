import re
import time
import yfinance as yf

# Per-ticker headline cache: ticker -> (fetched_at_epoch, headlines). yfinance's .news
# endpoint is unofficial/undocumented with no published rate limit, and the screener
# refreshes every 15s, so this collapses repeated same-ticker fetches within the TTL
# window down to one real network call.
_news_cache = {}


def _extract_url(content):
    canonical = content.get("canonicalUrl") or {}
    if canonical.get("url"):
        return canonical["url"]
    click_through = content.get("clickThroughUrl") or {}
    return click_through.get("url", "")


# yfinance's unofficial .news endpoint has no relatedTickers/relevance field to filter on
# (confirmed live 2026-07-13 by inspecting the raw response) - it returns Yahoo's general
# "trending stories shown on this ticker's page" carousel, not strictly single-company news.
# Caught live: obscure tickers returned headlines entirely about unrelated companies (Opendoor,
# generic "Most Active Stocks" market roundups) tagged as if they were that ticker's own news,
# which would have shown sentiment computed from headlines that have nothing to do with the
# stock. A whole-word match of the ticker symbol in the title/summary is an imperfect but honest
# relevance signal - it trades away some recall (a real headline that names the company instead
# of the ticker, e.g. "GameStop" instead of "GME", won't match) for not silently misattributing
# sentiment, matching this project's "missing beats fabricated" convention elsewhere.
def _mentions_ticker(text, ticker):
    if not text:
        return False
    return re.search(rf"\b{re.escape(ticker)}\b", text, re.IGNORECASE) is not None


def _fetch_single_ticker_news(ticker):
    try:
        raw_items = yf.Ticker(ticker).news or []
    except Exception as e:
        print(f"⚠️ Error fetching yfinance news for {ticker}: {e}")
        return []

    headlines = []
    for item in raw_items:
        content = item.get("content", {}) or {}
        title = content.get("title", "")
        summary = content.get("summary", "")
        if not (_mentions_ticker(title, ticker) or _mentions_ticker(summary, ticker)):
            continue
        headlines.append({
            "headline": title or "No title",
            "timestamp": content.get("pubDate", "Unknown time"),
            "url": _extract_url(content),
            "tickers": [ticker]
        })
    return headlines


# Fetches recent news for a list of tickers via yfinance's free, keyless .news
# property, returning the same shape as finviz_api.fetch_all_finviz_api_news()
# so it's a drop-in replacement value-shape-wise. Unlike Finviz's single bulk
# export, yfinance has no market-wide news call, so this fetches per ticker.
def fetch_yfinance_news(tickers, cache_ttl_seconds=600):
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
