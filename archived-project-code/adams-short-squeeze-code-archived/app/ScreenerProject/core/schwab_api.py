import base64
import json
import os
import statistics
import threading
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv

from core.filters import compute_target_stop
from core.provider_utils import is_valid_number
from core.scoring import score_setup
from core.short_interest import (
    calculate_days_to_cover,
    calculate_short_float_percent,
    check_short_float_discrepancy,
)
from core.technical_indicators import compute_rsi, compute_weekly_volatility, compute_ttm_squeeze
from core.yfinance_float_api import get_float_stats

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# App credentials from the Schwab Developer Portal app (Trader API - Individual, see
# PROJECT_NOTES.md §7/§9). Blank until the app is created and its Client ID/Secret are copied
# into .env - every function below degrades to "not configured"/"not available" rather than
# raising until then, the same opportunistic pattern as FINVIZ_API_KEY/NEWSAPI_KEY.
APP_KEY = os.environ.get("SCHWAB_APP_KEY", "")
APP_SECRET = os.environ.get("SCHWAB_APP_SECRET", "")
# Must match, character-for-character (including scheme and absence of a trailing slash), the
# Callback URL registered on the app - https://127.0.0.1:8182 is the community-standard default
# for a local single-user app (confirmed against Schwab's own docs 2026-07-13: only 127.0.0.1 is
# permitted as the host).
CALLBACK_URL = os.environ.get("SCHWAB_CALLBACK_URL") or "https://127.0.0.1:8182"

# Confirmed live against Schwab's public Trader API documentation/OpenAPI spec, 2026-07-13 -
# not guessed. Only the authorization_code/refresh_token grants are used; there is no other
# OAuth flow available for Schwab's APIs.
AUTHORIZE_URL = "https://api.schwabapi.com/v1/oauth/authorize"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
MARKET_DATA_BASE_URL = "https://api.schwabapi.com/marketdata/v1"

# Local token cache - never committed (data/* is gitignored except data/labeled_data.csv, see
# .gitignore). Holds only the access/refresh tokens and when they were minted; never the app
# secret itself (that stays in .env).
TOKEN_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schwab_tokens.json")

# Schwab-documented limits, confirmed 2026-07-13 (schwab-py's docs, matching Schwab's own): access
# tokens last 30 minutes; refresh tokens hard-expire after 7 days with no way to renew past that -
# a fresh browser login (core/schwab_auth.py) is required roughly weekly, not just once ever.
ACCESS_TOKEN_LIFETIME_SECONDS = 30 * 60
REFRESH_TOKEN_LIFETIME_SECONDS = 7 * 24 * 3600
# Refresh a little before the real expiry so an in-flight request never straddles it.
ACCESS_TOKEN_REFRESH_BUFFER_SECONDS = 60

# Discovery target, Schwab's closest analog to core/ib_api.py's TOP_PERC_GAIN/STK.US.MAJOR
# scanner. Path/query parameters confirmed against Schwab's public market-data OpenAPI spec,
# 2026-07-13: symbol_id one of $DJI/$COMPX/$SPX/NYSE/NASDAQ/OTCBB/INDEX_ALL/EQUITY_ALL/
# OPTION_ALL/OPTION_PUT/OPTION_CALL; sort one of VOLUME/TRADES/PERCENT_CHANGE_UP/
# PERCENT_CHANGE_DOWN. EQUITY_ALL + PERCENT_CHANGE_UP is the broadest "top gainers across major
# US stocks" equivalent to IB's scan. Unlike IB's scanner, movers has no server-side price-band
# filter - the $2-$20 band is applied client-side in run_scan_cycle() instead. Each screener
# entry's price field is "lastPrice" (confirmed live 2026-07-13 against the real endpoint - the
# public OpenAPI spec's schema names it "last", which does not match the actual response).
MOVERS_SYMBOL_ID = "EQUITY_ALL"
MOVERS_SORT = "PERCENT_CHANGE_UP"
MOVERS_FREQUENCY = 0

# Cached ~hourly per symbol, matching core/ib_api.py's HIST_CACHE_TTL_SECONDS rationale: RSI/
# volatility/average-volume don't need per-cycle freshness, and this keeps /pricehistory calls
# well under any reasonable per-minute rate limit.
HIST_CACHE_TTL_SECONDS = 3600
_hist_cache = {}  # symbol -> (fetched_at_epoch, {"rsi", "vol_w", "avg_volume", ...})

_state_lock = threading.Lock()
_latest_snapshot = []  # list of enriched per-ticker dicts, see _build_row()

# NOTE: order placement is intentionally not implemented anywhere in this module. This screener
# is read-only (PROJECT_NOTES.md §7) - only market-data/quote/history/movers endpoints are used.


def is_configured():
    """True once SCHWAB_APP_KEY/SCHWAB_APP_SECRET are set in .env - mirrors the opportunistic
    'is a real key present' checks controller.py already does for Finviz/NewsAPI."""
    return bool(APP_KEY and APP_SECRET)


def build_authorize_url():
    """The URL to open in a browser for the one-time manual OAuth consent step
    (see core/schwab_auth.py)."""
    return f"{AUTHORIZE_URL}?client_id={APP_KEY}&redirect_uri={CALLBACK_URL}"


def _basic_auth_header():
    credentials = f"{APP_KEY}:{APP_SECRET}".encode("utf-8")
    return {"Authorization": f"Basic {base64.b64encode(credentials).decode('utf-8')}"}


def _extract_code_from_redirect_url(redirect_url):
    query = parse_qs(urlparse(redirect_url).query)
    codes = query.get("code")
    if not codes:
        raise ValueError("No 'code' query parameter found in the pasted redirect URL.")
    return codes[0]


def _load_tokens():
    try:
        with open(TOKEN_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _save_tokens(tokens):
    os.makedirs(os.path.dirname(TOKEN_STORE_PATH), exist_ok=True)
    with open(TOKEN_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)


def _store_token_response(payload):
    now = time.time()
    existing = _load_tokens()
    tokens = {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token") or (existing or {}).get("refresh_token"),
        "access_token_fetched_at": now,
        # Schwab may rotate the refresh token on a refresh grant; only reset its own 7-day clock
        # if we actually got a *new* one, so a routine access-token refresh doesn't silently grant
        # extra runway on an unchanged refresh token.
        "refresh_token_fetched_at": now,
    }
    if existing and payload.get("refresh_token") == existing.get("refresh_token"):
        tokens["refresh_token_fetched_at"] = existing.get("refresh_token_fetched_at", now)
    _save_tokens(tokens)
    return tokens


def bootstrap_tokens_from_redirect_url(redirect_url):
    """One-time manual OAuth bootstrap - see core/schwab_auth.py. Exchanges the 'code' from the
    browser's post-consent redirect for an access+refresh token pair and caches them locally."""
    code = _extract_code_from_redirect_url(redirect_url)
    response = requests.post(
        TOKEN_URL,
        headers={**_basic_auth_header(), "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "authorization_code", "code": code, "redirect_uri": CALLBACK_URL},
        timeout=15,
    )
    response.raise_for_status()
    return _store_token_response(response.json())


def _refresh_access_token(tokens):
    response = requests.post(
        TOKEN_URL,
        headers={**_basic_auth_header(), "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]},
        timeout=15,
    )
    response.raise_for_status()
    return _store_token_response(response.json())


def _get_valid_access_token():
    tokens = _load_tokens()
    if not tokens:
        raise RuntimeError("Schwab is not yet authorized - run core/schwab_auth.py once.")

    now = time.time()
    refresh_token_age = now - tokens.get("refresh_token_fetched_at", 0)
    if refresh_token_age >= REFRESH_TOKEN_LIFETIME_SECONDS:
        raise RuntimeError(
            "Schwab's refresh token has passed its 7-day limit - re-run core/schwab_auth.py."
        )

    access_token_age = now - tokens.get("access_token_fetched_at", 0)
    if access_token_age >= (ACCESS_TOKEN_LIFETIME_SECONDS - ACCESS_TOKEN_REFRESH_BUFFER_SECONDS):
        tokens = _refresh_access_token(tokens)

    return tokens["access_token"]


def is_available():
    """Cheap, local-only check (no network call) - mirrors core/ib_api.py's is_ib_available().
    Used by controller.py's provider dispatch every cycle; actual auth failures surface via
    health()/exceptions at fetch time instead of a live probe here."""
    if not is_configured():
        return False
    tokens = _load_tokens()
    if not tokens:
        return False
    refresh_token_age = time.time() - tokens.get("refresh_token_fetched_at", 0)
    return refresh_token_age < REFRESH_TOKEN_LIFETIME_SECONDS


def health():
    """Provenance/status reporting (PROJECT_NOTES.md §7's 'health and provenance reporting'
    requirement) - call this from anywhere that needs to show setup progress without reading logs."""
    if not is_configured():
        return {"status": "not_configured", "detail": "SCHWAB_APP_KEY/SCHWAB_APP_SECRET not set in .env."}

    tokens = _load_tokens()
    if not tokens:
        return {"status": "not_yet_authorized", "detail": "Run core/schwab_auth.py once to complete the OAuth consent flow."}

    now = time.time()
    refresh_token_age = now - tokens.get("refresh_token_fetched_at", 0)
    if refresh_token_age >= REFRESH_TOKEN_LIFETIME_SECONDS:
        return {"status": "needs_reauth", "detail": "Refresh token is past Schwab's 7-day limit - re-run core/schwab_auth.py."}

    return {
        "status": "ready",
        "detail": None,
        "refresh_token_age_seconds": round(refresh_token_age, 1),
        "refresh_token_expires_in_seconds": round(REFRESH_TOKEN_LIFETIME_SECONDS - refresh_token_age, 1),
    }


# --- market data clients ---
# All synchronous (plain `requests`) - unlike core/ib_api.py's Gateway connection, Schwab's
# Trader API is stateless REST with short-lived OAuth tokens, so no persistent connection or
# background asyncio loop is needed; one call per controller.py refresh cycle is enough.

def _authorized_get(path, params=None):
    token = _get_valid_access_token()
    response = requests.get(
        f"{MARKET_DATA_BASE_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def fetch_movers(symbol_id=MOVERS_SYMBOL_ID, sort=MOVERS_SORT, frequency=MOVERS_FREQUENCY):
    """GET /movers/{symbol_id} - see the MOVERS_* constants above for the confirmed parameter spec."""
    data = _authorized_get(f"/movers/{symbol_id}", {"sort": sort, "frequency": frequency})
    return data.get("screeners", [])


def fetch_quotes(symbols):
    """GET /quotes?symbols=A,B,C - returns {symbol: {"quote": {...}, ...}}."""
    if not symbols:
        return {}
    return _authorized_get("/quotes", {"symbols": ",".join(symbols)})


def fetch_price_history(symbol):
    """30 daily bars, mirroring core/ib_api.py's reqHistoricalData call (durationStr='30 D',
    barSizeSetting='1 day') so RSI/weekly-volatility/average-volume are computed the same way
    regardless of which provider supplied the bars."""
    data = _authorized_get("/pricehistory", {
        "symbol": symbol,
        "periodType": "month",
        "period": 1,
        "frequencyType": "daily",
        "frequency": 1,
    })
    return data.get("candles", [])


def _hist_stats_from_candles(candles):
    if len(candles) < 2:
        return None

    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    squeeze_on, squeeze_momentum = compute_ttm_squeeze(highs, lows, closes)

    return {
        "rsi": compute_rsi(closes),
        "vol_w": compute_weekly_volatility(closes),
        "avg_volume": statistics.mean(volumes[:-1]) if len(volumes) > 1 else volumes[-1],
        "last_volume": volumes[-1],
        "last_close": closes[-1],
        "prev_close": closes[-2],
        "ttm_squeeze_on": squeeze_on,
        "ttm_squeeze_momentum": squeeze_momentum,
    }


def _get_hist_stats(symbol):
    now = time.time()
    cached = _hist_cache.get(symbol)
    if cached and (now - cached[0]) < HIST_CACHE_TTL_SECONDS:
        return cached[1]

    try:
        candles = fetch_price_history(symbol)
    except Exception as e:
        print(f"⚠️ Schwab price-history fetch failed for {symbol}: {e}")
        return None

    stats = _hist_stats_from_candles(candles)
    if stats is not None:
        _hist_cache[symbol] = (now, stats)
    return stats


# Builds one row in the same normalized shape as core/ib_api.py's _build_row() - this is the
# "provider contract" other code (controller.py, tests) relies on, so every field name/meaning
# here must match that shape exactly for the two providers to be truly interchangeable.
def _build_row(symbol, quote, hist):
    quote_body = quote.get("quote", {})
    last_price = quote_body.get("lastPrice")
    close_price = quote_body.get("closePrice")

    # Schwab's own borrow-availability signal (confirmed live 2026-07-13 in the real /quotes
    # response) - conceptually similar to IB's tick 236 shortable shares, but kept under its own
    # schwab_htb_* name rather than folded into ib_shortable_shares, since it's a different
    # provider's inventory figure, not IB's. Like ib_shortable_shares, this is a broker-specific
    # borrow signal, not official short interest - never substitute it for shares_short.
    reference = quote.get("reference", {})
    htb_quantity = reference.get("htbQuantity")
    htb_rate = reference.get("htbRate")
    is_hard_to_borrow = reference.get("isHardToBorrow")
    has_htb_data = any(v is not None for v in (htb_quantity, htb_rate, is_hard_to_borrow))
    schwab_htb_as_of = datetime.now(timezone.utc).isoformat() if has_htb_data else None

    price = last_price if is_valid_number(last_price) and last_price > 0 else hist["last_close"]
    prev_close = close_price if is_valid_number(close_price) and close_price > 0 else hist["prev_close"]
    if not prev_close:
        return None

    change_percent = round(((price - prev_close) / prev_close) * 100, 2)

    today_volume = hist["last_volume"]
    rel_volume = round(today_volume / hist["avg_volume"], 2) if hist["avg_volume"] else 0.0

    # Schwab's Trader API has no fundamentals/float or official short-interest endpoint - same
    # shared yfinance-backed lookup core/ib_api.py uses, see core/yfinance_float_api.py.
    float_stats = get_float_stats(symbol)
    float_shares = float_stats["float_shares"]
    provider_short_percent = float_stats["short_percent"]
    shares_short = float_stats["shares_short"]
    short_interest_as_of = float_stats["short_interest_as_of"]
    float_as_of = datetime.fromtimestamp(float_stats["_fetched_at"], timezone.utc).isoformat()

    calculated_short_percent, _calc_reason = calculate_short_float_percent(shares_short, float_shares)
    days_to_cover, _dtc_reason = calculate_days_to_cover(shares_short, hist["avg_volume"])

    # Schwab has no broker-inventory/shortable-shares equivalent to IB's tick 236 - keep the key
    # present (None) rather than omitted, so every provider's row has an identical key set.
    quality_flags = ["ib_shortable_shares_not_applicable_schwab"]
    if calculated_short_percent is not None:
        short_float_percent_value = calculated_short_percent
        discrepancy_flag = check_short_float_discrepancy(calculated_short_percent, provider_short_percent)
        if discrepancy_flag:
            quality_flags.append(discrepancy_flag)
    else:
        short_float_percent_value = provider_short_percent
        if short_float_percent_value is not None:
            quality_flags.append("short_float_percent_provider_supplied")
    if shares_short is None:
        quality_flags.append("shares_short_unavailable")
    if days_to_cover is None:
        quality_flags.append("days_to_cover_unavailable")
    if not has_htb_data:
        quality_flags.append("schwab_htb_unavailable")
    if hist["ttm_squeeze_on"] is None:
        quality_flags.append("ttm_squeeze_unavailable")  # fewer than 21 daily bars available yet

    return {
        "ticker": symbol,
        "price": str(price),
        "float_shares": str(float_shares) if float_shares is not None else "N/A",
        "rel_volume": str(rel_volume),
        "change_percent": str(change_percent),
        "short_float_percent": str(short_float_percent_value) if short_float_percent_value is not None else "N/A",
        "shares_short": shares_short,
        "days_to_cover": days_to_cover,
        "short_interest_as_of": short_interest_as_of,
        "short_interest_source": "yfinance" if shares_short is not None else None,
        "float_source": "yfinance",
        "float_as_of": float_as_of,
        "ib_shortable_shares": None,
        "ib_shortable_shares_as_of": None,
        "schwab_htb_quantity": htb_quantity,
        "schwab_htb_rate": htb_rate,
        "schwab_is_hard_to_borrow": is_hard_to_borrow,
        "schwab_htb_as_of": schwab_htb_as_of,
        "ttm_squeeze_on": hist["ttm_squeeze_on"],
        "ttm_squeeze_momentum": hist["ttm_squeeze_momentum"],
        "quality_flags": quality_flags,
        "_price_num": price,
        "_change_num": change_percent,
        "_relvol_num": rel_volume,
        "_shortfloat_num": short_float_percent_value if short_float_percent_value is not None else 0.0,
        "_vol_w": hist["vol_w"],
        "_rsi": hist["rsi"],
    }


def run_scan_cycle():
    """Synchronous end-to-end scan: movers -> $2-$20 price-band prefilter -> quote+history
    enrichment -> normalized rows cached in _latest_snapshot. Unlike core/ib_api.py's background
    asyncio loop, Schwab's stateless REST + short-lived tokens need no persistent
    connection/thread - this runs once per controller.py refresh cycle, called directly from
    rank_and_group_stocks_schwab()."""
    try:
        movers = fetch_movers()
    except Exception as e:
        print(f"⚠️ Schwab movers fetch failed: {e}")
        return

    candidates = [
        m["symbol"] for m in movers
        if m.get("symbol") and is_valid_number(m.get("lastPrice")) and 2.0 <= m["lastPrice"] <= 20.0
    ]
    if not candidates:
        with _state_lock:
            _latest_snapshot.clear()
        return

    try:
        quotes = fetch_quotes(candidates)
    except Exception as e:
        print(f"⚠️ Schwab quotes fetch failed: {e}")
        return

    rows = []
    for symbol in candidates:
        quote = quotes.get(symbol)
        if not quote:
            continue
        hist = _get_hist_stats(symbol)
        if hist is None:
            continue
        row = _build_row(symbol, quote, hist)
        if row is not None:
            rows.append(row)

    with _state_lock:
        _latest_snapshot.clear()
        _latest_snapshot.extend(rows)


# Same output shape as core/ib_api.py's rank_and_group_stocks_ib() and core/filters.py's
# rank_and_group_stocks() - a flat list of candidate dicts, not pre-split into Prime/Subprime -
# so controller.py can call whichever provider is available through this identical interface
# without any provider-specific branching beyond picking which one to call (see controller.py's
# _provider_table()). Tier classification (2026-07-17 redesign,
# SQUEEZE_FORMULA_REDESIGN_HANDOFF.md) now happens once, cross-provider, in controller.py via
# core/squeeze_score.py::classify_tier() off the composite squeeze score - not here via
# score_setup(), which is no longer called from this function (it's still used below, unchanged,
# by score_tickers_for_corroboration()).
def rank_and_group_stocks_schwab():
    run_scan_cycle()
    with _state_lock:
        snapshot = list(_latest_snapshot)

    candidates = []
    for s in snapshot:
        target, stop = compute_target_stop(s["_vol_w"], s["_rsi"])

        stock_data = {
            "Ticker": s["ticker"],
            "Price": s["price"],
            "Float": s["float_shares"],
            "RelVolume": s["rel_volume"],
            "ChangePercent": s["change_percent"],
            "ShortFloat": s["short_float_percent"],
            "Target": target,
            "StopLoss": stop,
            "Headline": None,
            "SharesShort": s.get("shares_short"),
            "DaysToCover": s.get("days_to_cover"),
            "ShortInterestAsOf": s.get("short_interest_as_of"),
            "ShortInterestSource": s.get("short_interest_source"),
            "FloatAsOf": s.get("float_as_of"),
            "FloatSource": s.get("float_source"),
            "IbShortableShares": s.get("ib_shortable_shares"),
            "IbShortableSharesAsOf": s.get("ib_shortable_shares_as_of"),
            "SchwabHtbQuantity": s.get("schwab_htb_quantity"),
            "SchwabHtbRate": s.get("schwab_htb_rate"),
            "SchwabIsHardToBorrow": s.get("schwab_is_hard_to_borrow"),
            "SchwabHtbAsOf": s.get("schwab_htb_as_of"),
            "TtmSqueezeOn": s.get("ttm_squeeze_on"),
            "TtmSqueezeMomentum": s.get("ttm_squeeze_momentum"),
            # IB-only field (core/ib_borrow_rate.py, IB's own FTP-fed stock-loan cost) - kept
            # present as None here too so every provider's row has an identical key set.
            "IbBorrowFeeRate": None,
            "IbBorrowRebateRate": None,
            "IbBorrowRateAsOf": None,
            "QualityFlags": s.get("quality_flags", []),
        }

        candidates.append(stock_data)

    return candidates


def score_tickers_for_corroboration(tickers):
    """For each ticker, independently fetch Schwab's own quote/history/float data and recompute
    the shared score_setup() rubric against it - used for cross-provider corroboration only.
    Unlike run_scan_cycle(), this never calls fetch_movers() or the price-band prefilter; the
    caller already knows which tickers it cares about (e.g. IB's already-flagged Prime/Subprime
    list that cycle), so cost scales with len(tickers), not the whole market.

    Returns {ticker: {"score": int, "schwab_htb_quantity", "schwab_htb_rate",
    "schwab_is_hard_to_borrow", "schwab_htb_as_of"}} for tickers Schwab could score - the HTB
    fields are already computed by _build_row() as part of scoring (found live 2026-07-16: this
    used to discard them and return a bare score, so Schwab's hard-to-borrow signal never
    surfaced on IB-sourced rows even when IB won the cycle's provider dispatch and corroboration
    ran). A ticker that errors or lacks data is simply omitted rather than raising - a Schwab
    hiccup must never break an already-good IB row."""
    if not tickers:
        return {}
    try:
        quotes = fetch_quotes(tickers)
    except Exception as e:
        print(f"⚠️ Schwab corroboration quotes fetch failed: {e}")
        return {}

    results = {}
    for ticker in tickers:
        quote = quotes.get(ticker)
        if not quote:
            continue
        try:
            hist = _get_hist_stats(ticker)
            if hist is None:
                continue
            row = _build_row(ticker, quote, hist)
            if row is None:
                continue
            results[ticker] = {
                "score": score_setup(
                    row["_price_num"], row["_change_num"], row["_relvol_num"], row["_shortfloat_num"]
                ),
                "schwab_htb_quantity": row["schwab_htb_quantity"],
                "schwab_htb_rate": row["schwab_htb_rate"],
                "schwab_is_hard_to_borrow": row["schwab_is_hard_to_borrow"],
                "schwab_htb_as_of": row["schwab_htb_as_of"],
            }
        except Exception as e:
            print(f"⚠️ Schwab corroboration scoring failed for {ticker}: {e}")

    return results
