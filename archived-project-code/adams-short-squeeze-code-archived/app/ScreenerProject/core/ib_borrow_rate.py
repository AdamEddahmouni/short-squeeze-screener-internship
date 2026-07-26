import asyncio
import ftplib
import io
import threading
import time
from datetime import datetime, timezone

# Live(r) short-squeeze pressure signal, requested by the advisor 2026-07-16: official
# shares_short (core/short_interest.py) is FINRA-reported twice a month and can't show a squeeze
# building today. IB publishes its own indicative stock-loan borrow cost via a public FTP feed -
# completely separate from the TWS/IB Gateway socket connection (core/ib_api.py) everything else
# in this app uses. A rising fee_rate means rising demand to borrow/short the stock - the same
# "lending cost" proxy IB's own site describes. Confirmed against IB's own FTP documentation
# and a cross-checked open-source reference implementation (2026-07-16); NOT independently
# verified live from this codebase's dev environment, whose network sandbox blocks outbound FTP
# (port 21) entirely - verify actual connectivity from a normal machine before relying on this.
FTP_HOST = "ftp3.interactivebrokers.com"
FTP_USER = "shortstock"
FTP_FILE = "usa.txt"
FETCH_TIMEOUT_SECONDS = 20

# IB's own FTP instructions: this file is regenerated hourly from 1am-11pm ET (Sun-Fri), and
# every 15 minutes from 4pm-6pm ET - not literally continuous, but far more frequent than
# official short interest. Cached to roughly match that cadence so a 15-second scan cycle isn't
# re-downloading a many-thousand-row file every pass for data that mostly doesn't change that
# often.
CACHE_TTL_SECONDS = 15 * 60

_cache_lock = threading.Lock()
_cached_at = 0.0
_rates_by_symbol = {}
_last_fetch_error = None


def _fetch_raw():
    """One blocking FTP round-trip - anonymous-style login (no password), download usa.txt into
    memory. Callers should run this off the calling thread/event loop (see get_borrow_rate())."""
    ftp = ftplib.FTP(FTP_HOST, timeout=FETCH_TIMEOUT_SECONDS)
    try:
        ftp.login(FTP_USER)
        buffer = io.BytesIO()
        ftp.retrbinary(f"RETR {FTP_FILE}", buffer.write)
    finally:
        ftp.close()
    return buffer.getvalue().decode("utf-8", errors="replace")


def _parse(raw_text):
    """IB's pipe-delimited feed: a timestamp/BOF line, a column-header line, one data row per
    shortable symbol (SYM|CUR|NAME|CON|ISIN|REBATERATE|FEERATE|AVAILABLE|...), then '#EOF' and a
    trailing blank line. Skips anything that isn't a well-formed data row rather than raising -
    one malformed line (or IB changing the trailing-field count) must not lose the whole feed."""
    rates = {}
    lines = raw_text.splitlines()
    for line in lines[2:]:  # skip the BOF timestamp line and the column-header line
        if not line or line.startswith("#"):
            continue
        fields = line.split("|")
        if len(fields) < 8:
            continue
        symbol, _cur, _name, _con, _isin, rebate, fee, available = fields[:8]
        try:
            rates[symbol] = {
                "fee_rate": float(fee) if fee else None,
                "rebate_rate": float(rebate) if rebate else None,
                "available": int(float(available)) if available else None,
            }
        except ValueError:
            continue
    return rates


def _refresh_if_stale():
    global _cached_at, _rates_by_symbol, _last_fetch_error
    with _cache_lock:
        if _rates_by_symbol and (time.time() - _cached_at) < CACHE_TTL_SECONDS:
            return

    try:
        parsed = _parse(_fetch_raw())
    except Exception as e:
        _last_fetch_error = str(e)
        print(f"⚠️ IB borrow-rate FTP fetch failed: {e}")
        return

    with _cache_lock:
        _rates_by_symbol = parsed
        _cached_at = time.time()
        _last_fetch_error = None


# Synchronous lookup - use from a synchronous caller. Refreshes the shared cache at most once
# per CACHE_TTL_SECONDS regardless of how many symbols are looked up in that window, so scanning
# 50 tickers a cycle costs one FTP download, not 50.
def get_borrow_rate(symbol):
    """Returns {"fee_rate", "rebate_rate", "available", "as_of"} - all None if the feed hasn't
    been fetched successfully yet or doesn't cover this symbol (e.g. it isn't shortable at all).
    fee_rate is IB's own indicative annualized borrow cost; a rising value signals rising demand
    to borrow/short the stock - never fabricated when the feed is unavailable."""
    _refresh_if_stale()
    with _cache_lock:
        entry = _rates_by_symbol.get(symbol)
        as_of = datetime.fromtimestamp(_cached_at, timezone.utc).isoformat() if _cached_at else None
    if entry is None:
        return {"fee_rate": None, "rebate_rate": None, "available": None, "as_of": None}
    return {**entry, "as_of": as_of}


async def get_borrow_rate_async(symbol):
    """asyncio wrapper for core/ib_api.py's event loop - offloads the blocking FTP call (only
    actually hits the network once per CACHE_TTL_SECONDS; a cache hit returns near-instantly but
    still runs off-thread for simplicity/consistency) via asyncio.to_thread, same pattern
    core/yfinance_float_api.py uses for its own blocking yfinance calls."""
    return await asyncio.to_thread(get_borrow_rate, symbol)
