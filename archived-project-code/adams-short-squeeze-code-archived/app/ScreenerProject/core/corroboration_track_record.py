import csv
import os

OUTCOMES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "corroboration_outcomes.csv")
OUTCOME_FIELDS = ["timestamp", "ticker", "corroboration_score", "logged_price", "current_price",
                   "pct_change", "benchmark_pct_change", "alpha_percent"]

# corroboration_score is always an integer 0-4 (controller.py's _apply_corroboration() rescores
# against the same 4-criteria rubric filters.py/ib_api.py/schwab_api.py already use) - discrete
# per-value bands, not ranges like the Squeeze Score's continuous 0-100 scale.
SCORE_BANDS = [4, 3, 2, 1, 0]


def score_band(score):
    rounded = round(score)
    return str(rounded) if rounded in SCORE_BANDS else "unknown"


def summarize_outcomes(path=OUTCOMES_PATH):
    """[{score_band, n, avg_change_percent, hit_rate_percent, avg_alpha_percent,
    beat_benchmark_rate_percent}, ...] ordered 4 -> 0, aggregated across every recorded outcome
    in data/corroboration_outcomes.csv (written by tests/evaluate_corroboration_outcomes.py).
    Empty list if nothing's been graded yet. Answers the advisor's own framing directly - "if IB
    and Schwab agree, we know we have the right to invest" - by checking whether a higher
    agreement score actually correlates with a better subsequent return, the same
    evidence-over-formula pattern as core/squeeze_score_track_record.py's summarize_outcomes(),
    which this mirrors, including the SPY-relative alpha keys added there 2026-07-17 (see that
    module's docstring for what alpha_percent means and why the two keys are omitted rather than
    null when no row in a band has a benchmark value yet).
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
            try:
                score = float(row["corroboration_score"])
            except (KeyError, TypeError, ValueError):
                continue
            bucket = by_band.setdefault(score_band(score), {"changes": [], "alphas": []})
            bucket["changes"].append(pct_change)
            try:
                bucket["alphas"].append(float(row["alpha_percent"]))
            except (KeyError, TypeError, ValueError):
                pass

    summary = []
    for band_value in SCORE_BANDS:
        label = str(band_value)
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
