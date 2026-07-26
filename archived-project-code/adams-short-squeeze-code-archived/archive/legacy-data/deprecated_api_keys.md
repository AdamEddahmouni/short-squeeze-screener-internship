# Deprecated Finviz API keys (consolidated 2026-07-08)

These keys were previously hardcoded directly in source files across `sentiment-rnd/`
and `archive/scripts/`. Both are dead (the Finviz Elite subscription they belonged to
has lapsed, confirmed in `PROJECT_NOTES.md` §4) and are no longer required —
discovery and news/sentiment now run on IB Gateway + yfinance with zero API keys
(see `PROJECT_NOTES.md` §8/§8a). Kept here, unredacted, as a single historical
record instead of scattered across files. Every source file that referenced one of
these now points back to this log instead of embedding the literal value.

Note: the NewsAPI key in `archive/scripts/Stock_sentiment_classifier_v2.py`
(`46437b2f8e5045d097b85ddfbd92ced7`) is deliberately **not** included here — per
`PROJECT_NOTES.md` §8a it tested live (`200 OK`) on 2026-07-07, unlike these two, so
it isn't dead and wasn't in scope for this cleanup.

## Finviz Elite API keys

- `750b45bf-5158-4678-b841-b695656321df`
  Previously in: `sentiment-rnd/Stock-News-ML/Negative_source.py`, `Positive_source.py`,
  `Neutral_source.py`, `archive/scripts/Negative_Sourcer.py`

- `d20e04ee-c9dd-4077-bac0-6139037bafd2`
  Previously in: `sentiment-rnd/Stock-News-ML/AI_ML_News_Alert.py`, `News_sourcer`,
  `archive/scripts/Formula_logger.py`
