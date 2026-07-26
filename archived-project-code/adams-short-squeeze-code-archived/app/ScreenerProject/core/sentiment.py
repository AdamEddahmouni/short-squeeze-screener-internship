import os
import pandas as pd
from transformers import pipeline
from textblob import TextBlob

# FinBERT: pretrained BERT fine-tuned on financial text (Financial PhraseBank + analyst
# reports), 3-class positive/negative/neutral. Replaces the old TF-IDF+RandomForest model
# that was trained on only ~823 generic headlines and collapsed neutral into negative.
FINBERT_MODEL = "ProsusAI/finbert"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FINETUNED_MODEL_DIR = os.path.join(BASE_DIR, "model", "finbert_finetuned")

_LABEL_MAP = {
    "positive": "\U0001F4C8 Positive",
    "negative": "\U0001F4C9 Negative",
    "neutral": "\U0001F610 Neutral",
}

# Weight given to the fine-tuned model's probability distribution vs. the zero-shot base model's
# when ensembling both - the fine-tuned model measurably outperforms zero-shot on this app's data
# (PROJECT_NOTES.md §8d/§8e/§8f), so it dominates the blend rather than being diluted 50/50.
FINETUNED_WEIGHT = 0.8


def _score_distribution(pipe, headlines):
    raw = pipe(headlines, truncation=True, top_k=None)
    return [{item["label"]: item["score"] for item in per_headline} for per_headline in raw]


# Classifies a list of headlines using the loaded model(s) and returns predictions + sentiment
# score. `model` is always {'primary': pipeline, 'secondary': pipeline_or_None} - when a secondary
# model is present its probability distribution is blended into the primary's (see
# FINETUNED_WEIGHT) rather than switching code paths, so this function has one consistent path
# regardless of whether ensembling is active.
def classify_headlines(headlines, model, vectorizer):
    if not headlines:
        return pd.DataFrame()

    primary_scores = _score_distribution(model["primary"], headlines)
    secondary = model.get("secondary")
    if secondary is not None:
        secondary_scores = _score_distribution(secondary, headlines)
        blended = [
            {label: FINETUNED_WEIGHT * p[label] + (1 - FINETUNED_WEIGHT) * s[label] for label in p}
            for p, s in zip(primary_scores, secondary_scores)
        ]
    else:
        blended = primary_scores

    results = []
    for headline, scores in zip(headlines, blended):
        top_label = max(scores, key=scores.get)
        results.append({
            "headline": headline,
            "sentiment_score": round(TextBlob(headline).sentiment.polarity, 3),
            "prediction": _LABEL_MAP[top_label],
            "confidence_score": round(scores[top_label], 3)
        })

    return pd.DataFrame(results)


# Loads the FinBERT sentiment-analysis pipeline(s) - the fine-tuned checkpoint
# (tests/finetune_sentiment.py's output) as primary if one has been trained and saved, otherwise
# the plain pretrained model. `ensemble=True` additionally loads the zero-shot base model as a
# secondary signal blended into every classify_headlines() call.
#
# Whether ensembling actually helps has flipped as the training data grew - on a smaller/weaker
# fine-tune (917 rows) the ensemble measurably beat fine-tuned-alone (68.75% vs 66.45% accuracy),
# but on the larger, better-trained checkpoint (1165 rows) fine-tuned-alone is now ahead (72.3% vs
# 71.1%, PROJECT_NOTES.md §8g) - blending in the comparatively weaker zero-shot model now drags
# the stronger fine-tuned model down rather than helping it. Default is `False` to match the
# current measurement; re-run tests/test_sentiment_finbert.py after any future data/training
# change to check whether that's still true; don't assume either direction is a fixed fact.
# `vectorizer` is unused - kept only so the 2-tuple unpack at the call site
# (`self.model, self.vectorizer = train_or_load_model()`) doesn't need to change.
def train_or_load_model(ensemble=False):
    has_finetuned = os.path.isdir(FINETUNED_MODEL_DIR)
    source = FINETUNED_MODEL_DIR if has_finetuned else FINBERT_MODEL
    primary = pipeline("sentiment-analysis", model=source, tokenizer=source)

    secondary = None
    if ensemble and has_finetuned:
        secondary = pipeline("sentiment-analysis", model=FINBERT_MODEL, tokenizer=FINBERT_MODEL)

    return {"primary": primary, "secondary": secondary}, None
