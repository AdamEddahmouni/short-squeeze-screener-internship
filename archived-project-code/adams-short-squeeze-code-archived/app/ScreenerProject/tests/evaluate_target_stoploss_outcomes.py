import csv
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yfinance as yf

# Validates the OTHER unvalidated formula PROJECT_NOTES.md §5 flags ("Target/stop-loss formula is
# a rough heuristic, not a validated model... derived by feeding a small personal spreadsheet into
# ChatGPT for curve-fitting") - same evidence-over-formula pattern as
# evaluate_squeeze_score_outcomes.py, different question: of the picks logged to prime_log.csv,
# did the price actually reach the target level before the stop-loss level, using each day's real
# high/low (not just a single later snapshot)? Not wired into the main app loop; run
# manually/periodically as prime_log.csv accumulates.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIME_LOG_PATH = os.path.join(BASE_DIR, "data", "prime_log.csv")
OUTCOMES_PATH = os.path.join(BASE_DIR, "data", "target_stoploss_outcomes.csv")
OUTCOME_FIELDS = ["timestamp", "ticker", "logged_price", "target_price", "stop_price",
                   "outcome", "hit_date"]

# Only grade rows old enough for "what happened next" to mean something - matches
# evaluate_sentiment_outcomes.py's/evaluate_squeeze_score_outcomes.py's own bar.
MIN_AGE = timedelta(days=1)
# A pick that's touched neither level after this long stops getting rechecked every run and is
# recorded as "expired" instead - otherwise a flat/quiet ticker gets re-fetched from yfinance
# forever.
MAX_AGE = timedelta(days=15)


def first_level_hit(bars, target_price, stop_price):
    """bars: [(date, high, low), ...] oldest-first. Returns (outcome, date):
    ('target', d) - the day's high reached target_price first
    ('stop', d)   - the day's low breached stop_price first
    ('both', d)   - same day crossed both (daily bars can't order intraday, so this is genuinely
                    ambiguous and excluded from win-rate math, not guessed at)
    (None, None)  - neither level touched in the given bars yet
    """
    for date, high, low in bars:
        hit_target = high >= target_price
        hit_stop = low <= stop_price
        if hit_target and hit_stop:
            return "both", date
        if hit_target:
            return "target", date
        if hit_stop:
            return "stop", date
    return None, None


def _already_scored_keys():
    if not os.path.exists(OUTCOMES_PATH):
        return set()
    with open(OUTCOMES_PATH, "r", newline="", encoding="utf-8") as f:
        return {(row["timestamp"], row["ticker"]) for row in csv.DictReader(f)}


def _daily_bars_since(ticker, since_date):
    try:
        history = yf.Ticker(ticker).history(start=since_date, interval="1d")
        if history.empty:
            return []
        return [
            (index.date().isoformat(), float(row["High"]), float(row["Low"]))
            for index, row in history.iterrows()
        ]
    except Exception as e:
        print(f"⚠️ Error fetching daily history for {ticker}: {e}")
        return []


def _print_summary():
    if not os.path.exists(OUTCOMES_PATH):
        return
    counts = {}
    with open(OUTCOMES_PATH, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            counts[row["outcome"]] = counts.get(row["outcome"], 0) + 1

    print("\nTarget/stop-loss outcomes (all recorded):")
    for label in ("target", "stop", "both", "expired"):
        if counts.get(label):
            print(f"  {label:>8}: {counts[label]}")

    graded = counts.get("target", 0) + counts.get("stop", 0)
    if graded:
        win_rate = 100 * counts.get("target", 0) / graded
        print(f"  Win rate (target-before-stop, excludes same-day/expired): "
              f"{counts.get('target', 0)}/{graded} ({win_rate:.1f}%)")


def main():
    if not os.path.exists(PRIME_LOG_PATH):
        print(f"No prime log yet at {PRIME_LOG_PATH} - nothing to evaluate.")
        return

    scored_keys = _already_scored_keys()
    now = datetime.now(timezone.utc)
    new_outcomes = []

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
            age = now - logged_at
            if age < MIN_AGE:
                continue

            try:
                logged_price = float(row["price"])
                target_percent = float(row["target"])
                stop_percent = float(row["stop_loss"])
            except (TypeError, ValueError, KeyError):
                continue

            target_price = round(logged_price * (1 + target_percent / 100), 4)
            stop_price = round(logged_price * (1 + stop_percent / 100), 4)

            bars = _daily_bars_since(row["ticker"], logged_at.date())
            outcome, hit_date = first_level_hit(bars, target_price, stop_price)

            if outcome is None:
                if age < MAX_AGE:
                    continue  # still pending - recheck on a future run
                outcome, hit_date = "expired", None

            new_outcomes.append({
                "timestamp": row["timestamp"],
                "ticker": row["ticker"],
                "logged_price": logged_price,
                "target_price": target_price,
                "stop_price": stop_price,
                "outcome": outcome,
                "hit_date": hit_date or "",
            })

    if not new_outcomes:
        print("No new prime_log.csv rows ready to grade yet.")
        return

    write_header = not os.path.exists(OUTCOMES_PATH)
    with open(OUTCOMES_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTCOME_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_outcomes)

    print(f"Scored {len(new_outcomes)} new row(s), appended to {OUTCOMES_PATH}")
    _print_summary()


if __name__ == "__main__":
    main()
