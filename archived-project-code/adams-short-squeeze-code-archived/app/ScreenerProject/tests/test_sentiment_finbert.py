import csv
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

from core.sentiment import train_or_load_model, classify_headlines, FINETUNED_MODEL_DIR

LABELED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labeled_data.csv")

# Persisted, append-only record of every comparison run - not just what happened to print to a
# terminal that session. CSV holds the summary metrics (one row per model per run, so accuracy/F1
# can be tracked over time as the model/data changes); TXT holds the full confusion matrix +
# per-class report for whoever wants the detail behind a given CSV row.
EVAL_LOG_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment_eval_log.csv")
EVAL_LOG_TXT = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment_eval_log.txt")
EVAL_LOG_FIELDS = [
    "run_timestamp", "model", "n_test_samples", "accuracy",
    "macro_precision", "macro_recall", "macro_f1", "weighted_f1",
    "positive_precision", "positive_recall", "positive_f1",
    "neutral_precision", "neutral_recall", "neutral_f1",
    "negative_precision", "negative_recall", "negative_f1",
]

# price_movement (1/0/-1) is the ground truth this whole comparison is judged against - both
# models are being asked "does this headline's sentiment match the labeled price direction?"
MOVEMENT_TO_LABEL = {1: "Positive", 0: "Neutral", -1: "Negative"}


def _log_results(model_name, true_labels, predictions, run_ts):
    report = classification_report(
        true_labels, predictions, labels=["Positive", "Neutral", "Negative"],
        zero_division=0, output_dict=True
    )
    matrix = confusion_matrix(true_labels, predictions, labels=["Positive", "Neutral", "Negative"])

    row = {
        "run_timestamp": run_ts,
        "model": model_name,
        "n_test_samples": len(true_labels),
        "accuracy": round(report["accuracy"], 4),
        "macro_precision": round(report["macro avg"]["precision"], 4),
        "macro_recall": round(report["macro avg"]["recall"], 4),
        "macro_f1": round(report["macro avg"]["f1-score"], 4),
        "weighted_f1": round(report["weighted avg"]["f1-score"], 4),
        "positive_precision": round(report["Positive"]["precision"], 4),
        "positive_recall": round(report["Positive"]["recall"], 4),
        "positive_f1": round(report["Positive"]["f1-score"], 4),
        "neutral_precision": round(report["Neutral"]["precision"], 4),
        "neutral_recall": round(report["Neutral"]["recall"], 4),
        "neutral_f1": round(report["Neutral"]["f1-score"], 4),
        "negative_precision": round(report["Negative"]["precision"], 4),
        "negative_recall": round(report["Negative"]["recall"], 4),
        "negative_f1": round(report["Negative"]["f1-score"], 4),
    }

    write_header = not os.path.exists(EVAL_LOG_CSV)
    with open(EVAL_LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVAL_LOG_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    with open(EVAL_LOG_TXT, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 70}\n{run_ts} - {model_name} ({len(true_labels)} test samples)\n{'=' * 70}\n")
        f.write("Confusion matrix (rows=true, cols=predicted; order Positive/Neutral/Negative):\n")
        f.write(f"{matrix}\n\n")
        f.write(classification_report(
            true_labels, predictions, labels=["Positive", "Neutral", "Negative"], zero_division=0
        ))
        f.write("\n")

    return row


# Reproduces the exact old TF-IDF + RandomForest pipeline (core/sentiment.py before the FinBERT
# swap), including the old classify_headlines()'s binary collapse (prediction == 1 -> Positive,
# else Negative) - so this baseline reflects what was actually shown to users, not just the raw
# model's training-time 3-class fit.
def old_model_predict(train_headlines, train_labels, test_headlines):
    vectorizer = TfidfVectorizer(stop_words="english")
    X_train = vectorizer.fit_transform(train_headlines)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, train_labels)

    X_test = vectorizer.transform(test_headlines)
    raw_predictions = model.predict(X_test)
    return ["Positive" if p == 1 else "Negative" for p in raw_predictions]


def new_model_predict(test_headlines, ensemble=False):
    model, vectorizer = train_or_load_model(ensemble=ensemble)
    df = classify_headlines(test_headlines, model, vectorizer)
    # Strip the emoji prefix ("📈 Positive" -> "Positive") to compare against MOVEMENT_TO_LABEL.
    return [p.split(" ", 1)[1] for p in df["prediction"]]


def main():
    run_ts = datetime.now().isoformat()
    df = pd.read_csv(LABELED_DATA_PATH, encoding="utf-8")
    df["true_label"] = df["price_movement"].map(MOVEMENT_TO_LABEL)

    train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)
    test_headlines = test_df["headline"].tolist()
    true_labels = test_df["true_label"].tolist()

    print(f"Evaluating on {len(test_headlines)} held-out headlines "
          f"(trained old baseline on {len(train_df)})...\n")

    print("=" * 70)
    print("OLD: TF-IDF + RandomForest (binary Positive/Negative, as actually shown to users)")
    print("=" * 70)
    old_predictions = old_model_predict(train_df["headline"], train_df["price_movement"], test_headlines)
    print(confusion_matrix(true_labels, old_predictions, labels=["Positive", "Neutral", "Negative"]))
    print(classification_report(true_labels, old_predictions, labels=["Positive", "Neutral", "Negative"], zero_division=0))
    old_row = _log_results("old_tfidf_randomforest", true_labels, old_predictions, run_ts)

    is_finetuned = os.path.isdir(FINETUNED_MODEL_DIR)
    new_model_name = "finbert_finetuned" if is_finetuned else "finbert_zeroshot"
    print("=" * 70)
    print(f"NEW: FinBERT ({'fine-tuned on labeled_data.csv' if is_finetuned else 'pretrained, zero-shot - never trained on this data'})")
    print("=" * 70)
    new_predictions = new_model_predict(test_headlines)
    print(confusion_matrix(true_labels, new_predictions, labels=["Positive", "Neutral", "Negative"]))
    print(classification_report(true_labels, new_predictions, labels=["Positive", "Neutral", "Negative"], zero_division=0))
    new_row = _log_results(new_model_name, true_labels, new_predictions, run_ts)

    ensemble_row = None
    if is_finetuned:
        print("=" * 70)
        print("ENSEMBLE: fine-tuned + zero-shot FinBERT blended (80/20)")
        print("=" * 70)
        ensemble_predictions = new_model_predict(test_headlines, ensemble=True)
        print(confusion_matrix(true_labels, ensemble_predictions, labels=["Positive", "Neutral", "Negative"]))
        print(classification_report(true_labels, ensemble_predictions, labels=["Positive", "Neutral", "Negative"], zero_division=0))
        ensemble_row = _log_results("finbert_ensemble", true_labels, ensemble_predictions, run_ts)

    print("=" * 70)
    print(f"Logged summary metrics to {EVAL_LOG_CSV}")
    print(f"Logged full confusion matrices + reports to {EVAL_LOG_TXT}")
    print(f"Accuracy: {old_row['accuracy']} -> {new_row['accuracy']}"
          + (f" -> {ensemble_row['accuracy']} (ensemble)" if ensemble_row else "")
          + f"  Macro F1: {old_row['macro_f1']} -> {new_row['macro_f1']}"
          + (f" -> {ensemble_row['macro_f1']} (ensemble)" if ensemble_row else ""))


if __name__ == "__main__":
    main()
