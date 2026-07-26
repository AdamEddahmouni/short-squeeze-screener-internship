import csv
import os
from datetime import datetime, timezone

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "squeeze_score_history.csv")
FIELDS = ["timestamp", "ticker", "squeeze_score"]


def append_scores(rows, path=HISTORY_PATH):
    """Append one row per (ticker, squeeze_score) pair for this scan cycle - a real time series,
    unlike controller.py's prime_log.csv (deduped to one row per ticker per day for alerting).
    Lets the web UI's Chart tab overlay how a ticker's Squeeze Score moved, not just its price.

    rows: iterable of (ticker, squeeze_score) tuples; entries with squeeze_score=None are skipped
    since compute_squeeze_score() returns None when an input is missing (core/squeeze_score.py) -
    logging that would just be a gap, not a real score of zero.
    """
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    write_header = not os.path.exists(path)
    timestamp = datetime.now(timezone.utc).isoformat()

    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        for ticker, score in rows:
            if score is None:
                continue
            writer.writerow({"timestamp": timestamp, "ticker": ticker, "squeeze_score": score})


def read_score_history(ticker, path=HISTORY_PATH):
    """[{timestamp, squeeze_score}] for one ticker, oldest first. Empty list if the file doesn't
    exist yet or nothing's been logged for this ticker - a valid "no history yet" state, not an
    error (mirrors snapshot_store.read_snapshot()'s empty-list convention). Tolerates a malformed
    row (matches log_prime_ticker()'s precedent - a bad prime_log.csv row previously crashed the
    whole refresh chain) by skipping just that row instead of raising.
    """
    if not os.path.exists(path):
        return []

    ticker = ticker.upper().strip()
    points = []
    with open(path, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row.get("ticker") != ticker:
                continue
            try:
                score = float(row["squeeze_score"])
            except (KeyError, TypeError, ValueError):
                continue
            points.append({"timestamp": row["timestamp"], "squeeze_score": score})
    return points
