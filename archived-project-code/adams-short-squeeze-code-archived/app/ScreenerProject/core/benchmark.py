import yfinance as yf

# Answers "compared to what?" for the Track Record panels - a hit rate or avg return means
# nothing on its own without a reference point (a rising tide lifts a random pick too). SPY is
# the standard, defensible choice: the whole market's return over the exact same holding period
# as each graded pick, not a hand-picked or after-the-fact-favorable comparison.
BENCHMARK_TICKER = "SPY"


def fetch_benchmark_daily_closes(start_date, ticker=BENCHMARK_TICKER):
    """{date: close} for every trading day from start_date to today. Empty dict on any fetch
    failure - callers treat a missing benchmark as "skip the comparison for this run", not a
    crash, same tolerance as the evaluators' own yfinance calls."""
    try:
        history = yf.Ticker(ticker).history(start=start_date, interval="1d")
        if history.empty:
            return {}
        return {index.date(): float(row["Close"]) for index, row in history.iterrows()}
    except Exception as e:
        print(f"⚠️ Error fetching benchmark ({ticker}) history: {e}")
        return {}


def close_at_or_before(daily_closes, date):
    """Latest close at or before `date` from a {date: close} dict, or None if nothing qualifies
    (mirrors the score_at_or_before pattern the evaluators already use for score history)."""
    match = None
    match_date = None
    for d, close in daily_closes.items():
        if d > date:
            continue
        if match_date is None or d > match_date:
            match_date = d
            match = close
    return match


def benchmark_pct_change(daily_closes, start_date, end_date):
    """% change of the benchmark from start_date to end_date (each resolved at-or-before, since
    a pick's exact logged date/today may fall on a non-trading day), or None if either endpoint
    isn't covered by daily_closes."""
    start_close = close_at_or_before(daily_closes, start_date)
    end_close = close_at_or_before(daily_closes, end_date)
    if start_close is None or end_close is None or start_close == 0:
        return None
    return round((end_close - start_close) / start_close * 100, 3)
