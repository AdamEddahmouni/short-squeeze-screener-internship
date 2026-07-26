import asyncio
import time

import yfinance as yf

from core.provider_utils import epoch_to_iso_date, is_valid_number

# Neither IB nor Schwab's Trader API expose float shares or the officially reported open short
# position (fundamentals aren't part of either account's market-data entitlement) - yfinance's
# free .info endpoint carries both for most US tickers, so every provider shares this one lookup
# instead of each reimplementing/re-fetching it independently. One shared cache also means a
# symbol scanned by more than one provider in the same run only costs one yfinance call.
#
# Cached far longer than any provider's own price/history cache: official short interest is only
# reported twice a month industry-wide, so this is a display/scoring nicety refreshed daily, not
# something that needs to track intraday - and yfinance's .info endpoint is slower and more
# rate-limit-prone than the lighter-weight calls providers make for price/volume.
FLOAT_CACHE_TTL_SECONDS = 24 * 3600
_float_cache = {}


def fetch_float_and_short_interest_stats(symbol):
    """One synchronous yfinance .info lookup - no caching. Most callers want
    get_float_stats()/get_float_stats_async() instead, which cache this."""
    try:
        info = yf.Ticker(symbol).info
    except Exception as e:
        print(f"⚠️ yfinance Float/Short-Interest lookup failed for {symbol}: {e}")
        return {"float_shares": None, "short_percent": None, "shares_short": None, "short_interest_as_of": None}

    float_shares = info.get("floatShares")
    short_fraction = info.get("shortPercentOfFloat")
    # yfinance reports this as a fraction (0.139); this app's scoring/display convention
    # (core/filters.py's clean_percent()) uses whole percent (13.9).
    short_percent = round(short_fraction * 100, 2) if is_valid_number(short_fraction) else None

    # sharesShort/dateShortInterest are yfinance's relay of the actual twice-monthly reported
    # open short position - the real shares_short input core/short_interest.py's formula needs,
    # not a proxy.
    shares_short = info.get("sharesShort")
    short_interest_as_of = epoch_to_iso_date(info.get("dateShortInterest"))

    return {
        "float_shares": float_shares,
        "short_percent": short_percent,
        "shares_short": shares_short if is_valid_number(shares_short) else None,
        "short_interest_as_of": short_interest_as_of,
    }


def get_float_stats(symbol):
    """Synchronous cached lookup - use this from a synchronous provider (core/schwab_api.py)."""
    now = time.time()
    cached = _float_cache.get(symbol)
    if cached and (now - cached[0]) < FLOAT_CACHE_TTL_SECONDS:
        fetched_at, stats = cached
        return {**stats, "_fetched_at": fetched_at}

    stats = fetch_float_and_short_interest_stats(symbol)
    _float_cache[symbol] = (now, stats)
    return {**stats, "_fetched_at": now}


async def get_float_stats_async(symbol):
    """asyncio wrapper for a provider running on an event loop (core/ib_api.py) - offloads the
    blocking yfinance call via asyncio.to_thread instead of stalling the loop. Shares the same
    cache/TTL as get_float_stats() so IB and Schwab scans of the same symbol don't double-fetch."""
    now = time.time()
    cached = _float_cache.get(symbol)
    if cached and (now - cached[0]) < FLOAT_CACHE_TTL_SECONDS:
        fetched_at, stats = cached
        return {**stats, "_fetched_at": fetched_at}

    stats = await asyncio.to_thread(fetch_float_and_short_interest_stats, symbol)
    _float_cache[symbol] = (now, stats)
    return {**stats, "_fetched_at": now}
