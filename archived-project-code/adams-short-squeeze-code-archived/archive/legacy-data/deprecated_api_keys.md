# Deprecated Finviz API keys (consolidated 2026-07-08)

These keys were previously hardcoded directly in source files across `sentiment-rnd/`
and `archive/scripts/`. Both are dead (the Finviz Elite subscription they belonged to
has lapsed, confirmed in `PROJECT_NOTES.md` §4) and are no longer required —
discovery and news/sentiment now run on IB Gateway + yfinance with zero API keys
(see `PROJECT_NOTES.md` §8/§8a). Kept here as a single historical record instead of
scattered across files. Every source file that referenced one of these now points back
to this log instead of embedding the literal value.

Note: a NewsAPI key was also present in `archive/scripts/Stock_sentiment_classifier_v2.py`
and has been redacted. Per `PROJECT_NOTES.md` §8a it tested live on 2026-07-07; rotate
at the provider if it was ever committed to version control.

## Finviz Elite API keys (redacted)

- Key A (formerly in `sentiment-rnd/Stock-News-ML/Negative_source.py`, `Positive_source.py`,
  `Neutral_source.py`, `archive/scripts/Negative_Sourcer.py`) — **revoked / lapsed**

- Key B (formerly in `sentiment-rnd/Stock-News-ML/AI_ML_News_Alert.py`, `News_sourcer`,
  `archive/scripts/Formula_logger.py`) — **revoked / lapsed**

Literal values are intentionally omitted from this public archive. Set `FINVIZ_API_KEY`
in your environment if you need to run legacy scripts locally.
