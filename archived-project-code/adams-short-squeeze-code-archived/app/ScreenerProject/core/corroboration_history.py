import csv
import os
from datetime import datetime, timezone

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "corroboration_history.csv")
FIELDS = ["timestamp", "ticker", "corroboration_score"]


def append_scores(rows, path=HISTORY_PATH):
    """Append one row per (ticker, corroboration_score) pair for this scan cycle - a real time
    series, same pattern as core/squeeze_score_history.py. Lets
    tests/evaluate_corroboration_outcomes.py check whether IB+Schwab agreement actually predicts
    better outcomes: the advisor's own explicit ask from a 2026-07-12 call ("if TD Ameritrade is
    telling me... and interactive broker is telling me... then we know we have the right to
    invest"), which has been labeled on every row (corroboration_score/corroborated_by) but never
    validated against real outcomes.

    rows: iterable of (ticker, corroboration_score) tuples; entries with corroboration_score=None
    are skipped - controller.py's _apply_corroboration() only computes a score when IB is the
    winning provider and Schwab is available that cycle, so None means "never checked", not "checked
    and disagreed" - logging it as a fake value would misrepresent that.
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
            writer.writerow({"timestamp": timestamp, "ticker": ticker, "corroboration_score": score})


def read_score_history(ticker, path=HISTORY_PATH):
    """[{timestamp, corroboration_score}] for one ticker, oldest first. Empty list if the file
    doesn't exist yet or nothing's been logged for this ticker - a valid "no history yet" state,
    not an error. Tolerates a malformed row by skipping just that row instead of raising, matching
    core/squeeze_score_history.py's precedent.
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
                score = float(row["corroboration_score"])
            except (KeyError, TypeError, ValueError):
                continue
            points.append({"timestamp": row["timestamp"], "corroboration_score": score})
    return points
