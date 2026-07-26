import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yfinance as yf

# controller.log_prime_ticker() already writes one row per prime ticker per day to
# prime_log.csv (timestamp, ticker, price, target, stop_loss, sentiment) - this script doesn't
# change that logging, it just reads the accumulated history and checks it against what
# actually happened. Not wired into the main app loop; run manually/periodically.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIME_LOG_PATH = os.path.join(BASE_DIR, "data", "prime_log.csv")
OUTCOMES_PATH = os.path.join(BASE_DIR, "data", "sentiment_outcomes.csv")
OUTCOME_FIELDS = ["timestamp", "ticker", "sentiment_label", "confidence", "logged_price",
                   "current_price", "pct_change", "direction_correct"]

# Only score rows old enough that "what happened next" is a real, settled answer rather than
# same-day noise.
MIN_AGE = timedelta(days=1)

SENTIMENT_RE = re.compile(r"(Positive|Neutral|Negative)\s*\((\d+)%\)")


def _parse_sentiment(sentiment_str):
    match = SENTIMENT_RE.search(sentiment_str or "")
    if not match:
        return None, None
    label, confidence = match.groups()
    return label, int(confidence) / 100


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


def main():
    if not os.path.exists(PRIME_LOG_PATH):
        print(f"No prime log yet at {PRIME_LOG_PATH} - nothing to evaluate.")
        return

    scored_keys = _already_scored_keys()
    now = datetime.now(timezone.utc)
    new_outcomes = []

    with open(PRIME_LOG_PATH, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["timestamp"], row["ticker"])
            if key in scored_keys:
                continue

            logged_at = datetime.fromisoformat(row["timestamp"])
            if logged_at.tzinfo is None:
                logged_at = logged_at.astimezone()
            if now - logged_at < MIN_AGE:
                continue

            label, confidence = _parse_sentiment(row.get("sentiment", ""))
            if label is None:
                continue

            try:
                logged_price = float(row["price"])
            except (TypeError, ValueError):
                continue

            current_price = _current_price(row["ticker"])
            if current_price is None or logged_price == 0:
                continue

            pct_change = round((current_price - logged_price) / logged_price * 100, 3)
            if label == "Positive":
                direction_correct = pct_change > 0
            elif label == "Negative":
                direction_correct = pct_change < 0
            else:  # Neutral makes no directional claim, so there's nothing to grade
                direction_correct = None

            new_outcomes.append({
                "timestamp": row["timestamp"],
                "ticker": row["ticker"],
                "sentiment_label": label,
                "confidence": confidence,
                "logged_price": logged_price,
                "current_price": current_price,
                "pct_change": pct_change,
                "direction_correct": direction_correct
            })

    if not new_outcomes:
        print("No new prime_log.csv rows old enough to score yet.")
        return

    write_header = not os.path.exists(OUTCOMES_PATH)
    with open(OUTCOMES_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTCOME_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_outcomes)

    graded = [o for o in new_outcomes if o["direction_correct"] is not None]
    correct = sum(1 for o in graded if o["direction_correct"])
    print(f"Scored {len(new_outcomes)} new row(s), appended to {OUTCOMES_PATH}")
    if graded:
        print(f"Directional accuracy this batch (Positive/Negative only): "
              f"{correct}/{len(graded)} ({round(100 * correct / len(graded), 1)}%)")


if __name__ == "__main__":
    main()
