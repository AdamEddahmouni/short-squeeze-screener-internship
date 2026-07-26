# Batch 13 News Integration

NewsAPI is constructed only from the production runtime configuration. Refresh stores
headline ID, headline, URL, publication time, retrieval time, ticker, and provider in a
per-symbol cache. Failures retain last-good data and store a redacted error.

The sanitized `AAPL` smoke returned 10 headlines with no authentication error. Tests use
`FakeNewsProvider` and deterministic data; they do not read the private file or use HTTP.

`news_count` is display-available. The canonical `catalyst` remains `UNKNOWN` when only
headline presence exists. Sentiment remains `NOT CONFIGURED`; FinBERT was deferred.
