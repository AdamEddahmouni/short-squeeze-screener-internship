import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from transformers import pipeline

from core.sentiment import FINBERT_MODEL

LABELED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labeled_data.csv")
FLAGGED_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "label_audit_flags.csv")

MOVEMENT_TO_LABEL = {1: "positive", 0: "neutral", -1: "negative"}

# Confident disagreement threshold: only flag rows where the *base, never-fine-tuned* FinBERT
# is quite sure the label is wrong, not just leaning that way. Using zero-shot rather than the
# fine-tuned checkpoint here deliberately - the fine-tuned model was trained on these exact
# labels, so checking it against them would partly just be checking whether it memorized them.
CONFIDENCE_THRESHOLD = 0.85


def main():
    df = pd.read_csv(LABELED_DATA_PATH, encoding="utf-8")
    df["true_label"] = df["price_movement"].map(MOVEMENT_TO_LABEL)

    print(f"Scoring {len(df)} headlines with zero-shot FinBERT...")
    model = pipeline("sentiment-analysis", model=FINBERT_MODEL, tokenizer=FINBERT_MODEL)
    predictions = model(df["headline"].tolist(), truncation=True)

    df["predicted_label"] = [p["label"] for p in predictions]
    df["predicted_confidence"] = [round(p["score"], 3) for p in predictions]

    flagged = df[
        (df["predicted_label"] != df["true_label"]) &
        (df["predicted_confidence"] >= CONFIDENCE_THRESHOLD)
    ].copy()

    flagged.to_csv(FLAGGED_OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nFlagged {len(flagged)}/{len(df)} rows where zero-shot FinBERT confidently "
          f"(>= {CONFIDENCE_THRESHOLD}) disagrees with the existing label.")
    print(f"Written to {FLAGGED_OUTPUT_PATH} for review.\n")

    for _, row in flagged.iterrows():
        print(f"[label={row['true_label']:8s} model={row['predicted_label']:8s} "
              f"conf={row['predicted_confidence']}]  {row['headline']}")


if __name__ == "__main__":
    main()
