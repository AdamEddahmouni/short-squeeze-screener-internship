import csv
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yfinance as yf

from core.benchmark import benchmark_pct_change, fetch_benchmark_daily_closes
from core.squeeze_score_track_record import OUTCOME_FIELDS, OUTCOMES_PATH, score_band, summarize_outcomes

# Cross-references two logs controller.py already writes every scan cycle:
# - prime_log.csv (timestamp, ticker, price, target, stop_loss, sentiment) - once per ticker/day
# - squeeze_score_history.csv (timestamp, ticker, squeeze_score) - every cycle,
#   core/squeeze_score_history.py
# Neither file carries the other's field, so this joins them by ticker + the latest logged score
# at-or-before the prime_log timestamp, then checks what the price actually did some days later
# (same "did it work" pattern as evaluate_sentiment_outcomes.py). This answers the advisor's own
# framing - "if the signal is real, we'll know we have the right to invest" - with recorded
# evidence instead of trusting the composite Squeeze Score formula (core/squeeze_score.py) on
# faith. Not wired into the main app loop; run manually/periodically as history accumulates.
# The outcomes schema/band math live in core/squeeze_score_track_record.py so api_server.py's web
# UI route can serve the exact same summary this script prints.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIME_LOG_PATH = os.path.join(BASE_DIR, "data", "prime_log.csv")
SCORE_HISTORY_PATH = os.path.join(BASE_DIR, "data", "squeeze_score_history.csv")

# Only score rows old enough that "what happened next" is a real, settled answer rather than
# same-day noise - matches evaluate_sentiment_outcomes.py's own bar.
MIN_AGE = timedelta(days=1)


def score_at_or_before(history_for_ticker, when):
    """Latest (datetime, score) pair at or before `when` from an oldest-first list, or None if
    history for this ticker starts after `when`."""
    match = None
    for ts, score in history_for_ticker:
        if ts > when:
            break
        match = score
    return match


def load_score_history(path=SCORE_HISTORY_PATH):
    """{ticker: [(datetime, score), ...]} sorted oldest-first. Tolerates a malformed row (skips
    it) rather than raising, matching core/squeeze_score_history.py's own read tolerance."""
    history = {}
    if not os.path.exists(path):
        return history
    with open(path, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                ts = datetime.fromisoformat(row["timestamp"])
                score = float(row["squeeze_score"])
            except (KeyError, TypeError, ValueError):
                continue
            history.setdefault(row["ticker"], []).append((ts, score))
    for rows in history.values():
        rows.sort(key=lambda pair: pair[0])
    return history


def _already_scored_keys():
    if not os.path.exists(OUTCOMES_PATH):
        return set()
    with open(OUTCOMES_PATH, "r", newline="", encoding="utf-8") as f:
        return {(row["timestamp"], row["ticker"]) for row in csv.DictReader(f)}


def _current_price(ticker):
    try:
        history = yf.Ticker(ticker).history(period="1d")
        if history.empty:
            return None
        return round(float(history["Close"].iloc[-1]), 4)
    except Exception as e:
        print(f"⚠️ Error fetching current price for {ticker}: {e}")
        return None


def _print_band_summary():
    """Avg return and hit-rate (pct_change > 0) by score band across ALL outcomes ever recorded,
    not just this run's batch - the point is watching this stabilize as more picks settle. Reuses
    core/squeeze_score_track_record.py's summarize_outcomes() so this printout and the web UI's
    Track Record panel (api_server.py's /squeeze-score-track-record route) never drift apart.
    Also prints the SPY-relative alpha when available (2026-07-17) - see that module's docstring."""
    summary = summarize_outcomes()
    if not summary:
        return
    print("\nSqueeze Score band performance (all recorded outcomes):")
    for row in summary:
        line = (f"  {row['score_band']:>6}: n={row['n']:<4} "
                f"avg_change={row['avg_change_percent']:+.2f}%  hit_rate={row['hit_rate_percent']:.1f}%")
        if "avg_alpha_percent" in row:
            line += (f"  vs SPY={row['avg_alpha_percent']:+.2f}%  "
                      f"beat_rate={row['beat_benchmark_rate_percent']:.1f}%")
        print(line)


def main():
    if not os.path.exists(PRIME_LOG_PATH):
        print(f"No prime log yet at {PRIME_LOG_PATH} - nothing to evaluate.")
        return

    history = load_score_history()
    if not history:
        print(f"No squeeze score history yet at {SCORE_HISTORY_PATH} - nothing to join against.")
        return

    scored_keys = _already_scored_keys()
    now = datetime.now(timezone.utc)
    new_outcomes = []

    # 90-day lookback is a generous fixed buffer, not a computed min-date - one SPY fetch reused
    # for every row this run, cheaper than a per-row network call and simpler than scanning
    # prime_log.csv twice just to find the true earliest date.
    daily_closes = fetch_benchmark_daily_closes((now - timedelta(days=90)).date())

    with open(PRIME_LOG_PATH, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row.get("timestamp"), row.get("ticker"))
            if key in scored_keys:
                continue

            try:
                logged_at = datetime.fromisoformat(row["timestamp"])
            except (KeyError, TypeError, ValueError):
                continue
            if logged_at.tzinfo is None:
                logged_at = logged_at.astimezone(timezone.utc)
            if now - logged_at < MIN_AGE:
                continue

            ticker = row["ticker"]
            score = score_at_or_before(history.get(ticker, []), logged_at)
            if score is None:
                continue

            try:
                logged_price = float(row["price"])
            except (TypeError, ValueError):
                continue

            current_price = _current_price(ticker)
            if current_price is None or logged_price == 0:
                continue

            pct_change = round((current_price - logged_price) / logged_price * 100, 3)
            bench_change = benchmark_pct_change(daily_closes, logged_at.date(), now.date())
            alpha = round(pct_change - bench_change, 3) if bench_change is not None else None

            new_outcomes.append({
                "timestamp": row["timestamp"],
                "ticker": ticker,
                "squeeze_score": score,
                "logged_price": logged_price,
                "current_price": current_price,
                "pct_change": pct_change,
                "score_band": score_band(score),
                "benchmark_pct_change": bench_change if bench_change is not None else "",
                "alpha_percent": alpha if alpha is not None else "",
            })

    if not new_outcomes:
        print("No new prime_log.csv rows old enough (with matching score history) to score yet.")
        return

    write_header = not os.path.exists(OUTCOMES_PATH)
    with open(OUTCOMES_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTCOME_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_outcomes)

    print(f"Scored {len(new_outcomes)} new row(s), appended to {OUTCOMES_PATH}")
    _print_band_summary()


if __name__ == "__main__":
    main()
