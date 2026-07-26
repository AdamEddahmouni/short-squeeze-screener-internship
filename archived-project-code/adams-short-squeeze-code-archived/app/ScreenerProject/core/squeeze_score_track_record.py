import csv
import os

OUTCOMES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "squeeze_score_outcomes.csv")
OUTCOME_FIELDS = ["timestamp", "ticker", "squeeze_score", "logged_price", "current_price",
                   "pct_change", "score_band", "benchmark_pct_change", "alpha_percent"]

# Ordered low-inclusive/high-exclusive bands matching core/squeeze_score.py's own documented
# tiers (90+ extreme, 70-89 high, 40-69 moderate, below 40 low).
SCORE_BANDS = [(90, 101, "90+"), (70, 90, "70-89"), (40, 70, "40-69"), (0, 40, "0-39")]


def score_band(score):
    for lo, hi, label in SCORE_BANDS:
        if lo <= score < hi:
            return label
    return "unknown"


def summarize_outcomes(path=OUTCOMES_PATH):
    """[{score_band, n, avg_change_percent, hit_rate_percent, avg_alpha_percent,
    beat_benchmark_rate_percent}, ...] ordered 90+ -> 0-39, aggregated across every recorded
    outcome in data/squeeze_score_outcomes.csv (written by tests/evaluate_squeeze_score_outcomes.py).
    Empty list if nothing's been graded yet - a valid "no evidence yet" state, not an error, same
    convention as snapshot_store.read_snapshot(). Shared by the CLI evaluator's own summary
    printout and api_server.py's web UI route so the band math only lives in one place.

    avg_alpha_percent/beat_benchmark_rate_percent (2026-07-17) answer "compared to what?" - a
    pick's own return means little without a reference point. alpha_percent is
    pct_change - benchmark_pct_change (core/benchmark.py, SPY over the same holding period),
    logged per-row by the evaluator. The two alpha keys are omitted entirely (not null) for a
    band where no row has a benchmark value yet, so the UI can tell "no comparison available"
    apart from "comparison is exactly zero."
    """
    if not os.path.exists(path):
        return []

    by_band = {}
    with open(path, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            try:
                pct_change = float(row["pct_change"])
            except (KeyError, TypeError, ValueError):
                continue
            bucket = by_band.setdefault(row.get("score_band"), {"changes": [], "alphas": []})
            bucket["changes"].append(pct_change)
            try:
                bucket["alphas"].append(float(row["alpha_percent"]))
            except (KeyError, TypeError, ValueError):
                pass

    summary = []
    for _, _, label in SCORE_BANDS:
        bucket = by_band.get(label)
        if not bucket or not bucket["changes"]:
            continue
        changes = bucket["changes"]
        avg = sum(changes) / len(changes)
        hit_rate = 100 * sum(1 for c in changes if c > 0) / len(changes)
        entry = {
            "score_band": label,
            "n": len(changes),
            "avg_change_percent": round(avg, 2),
            "hit_rate_percent": round(hit_rate, 1),
        }
        alphas = bucket["alphas"]
        if alphas:
            entry["avg_alpha_percent"] = round(sum(alphas) / len(alphas), 2)
            entry["beat_benchmark_rate_percent"] = round(
                100 * sum(1 for a in alphas if a > 0) / len(alphas), 1)
        summary.append(entry)
    return summary
