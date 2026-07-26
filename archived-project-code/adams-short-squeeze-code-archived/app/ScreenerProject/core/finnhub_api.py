import os
import time
import requests
from dotenv import load_dotenv

# Loaded here (not just in main.py) for the same reason as newsapi_news_api.py -
# FINNHUB_KEY needs to be populated regardless of entry point.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Free real-time price source, chained in ahead of IB's own delayed feed (this
# account has no real-time market-data entitlement - error 10089, see
# PROJECT_NOTES.md §8). Finnhub's free tier gives real-time US-equity quotes off
# the IEX feed (one exchange's tape, not the full consolidated one - still real-time,
# just not identical to a paid subscription) capped at 60 req/min, non-commercial use.
FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "")

MAX_REQUESTS_PER_MINUTE = 55  # margin under Finnhub's 60/min cap
_request_count = 0
_window_start = time.time()

# Short-lived cache, not the 24h-style cache used for float/short-interest -
# this is meant to track intraday price, so it's just here to keep a 50-ticker
# scanner batch (IB's SCANNER_ROWS) from blowing the per-minute quota if the
# enrichment loop's ENRICH_INTERVAL_SECONDS cadence overlaps a quota window.
QUOTE_CACHE_TTL_SECONDS = 15
_quote_cache = {}


def _reset_window_if_expired():
    global _request_count, _window_start
    now = time.time()
    if now - _window_start >= 60:
        _request_count = 0
        _window_start = now


def _quota_available():
    _reset_window_if_expired()
    return _request_count < MAX_REQUESTS_PER_MINUTE


# Fetches a real-time last price for one symbol via Finnhub's free /quote endpoint.
# Returns None (never raises) on any failure - missing key, exhausted quota, bad
# symbol, network error - so callers can fall straight through to the existing
# IB-delayed price path without special-casing this source. That fallback chain
# (Finnhub -> IB delayed tick -> IB historical close) is what actually lives in
# core/ib_api.py's _build_row(); this module only owns the Finnhub leg of it.
def fetch_finnhub_price(symbol):
    global _request_count
    if not FINNHUB_KEY:
        return None

    now = time.time()
    cached = _quote_cache.get(symbol)
    if cached and (now - cached[0]) < QUOTE_CACHE_TTL_SECONDS:
        return cached[1]

    if not _quota_available():
        return None

    try:
        response = requests.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": FINNHUB_KEY},
            timeout=5,
        )
        _request_count += 1
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"⚠️ Finnhub price lookup failed for {symbol}: {e}")
        return None

    price = data.get("c")  # "current price" per Finnhub's /quote response schema
    if not price or price <= 0:
        return None

    _quote_cache[symbol] = (now, price)
    return price
