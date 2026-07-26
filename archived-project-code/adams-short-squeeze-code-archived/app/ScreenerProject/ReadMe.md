# 🧠 Stock Screener with Sentiment Analysis

A live short squeeze screener that discovers candidates via Interactive Brokers' scanner, matches
them against real news headlines (yfinance, free/keyless), applies AI-driven sentiment
classification, and auto-calculates price targets and stop-losses. Finviz Elite is supported as an
optional, opportunistic data source (used automatically if a real API key is configured) but is
**not required** — see "Data sources" below.

---

## 🚀 Features

- ✅ Real-time discovery via Interactive Brokers' scanner (no Finviz key needed) — `core/ib_api.py`
- ✅ Free, keyless news fetching via `yfinance` (no Finviz key needed) — `core/yfinance_news_api.py`
- ✅ Optional Finviz Elite integration, used automatically if a real API key is configured
- ✅ Custom filters for float, price, % change, short float, and relative volume
- ✅ Sentiment analysis on breaking news headlines via pretrained FinBERT (positive/neutral/negative)
- ✅ Color-coded GUI with Prime vs Subprime setup detection
- ✅ Short-float percentage shown in the GUI and included in integration snapshots
- ✅ Automatic logging of top setups
- ✅ Target and stop-loss calculation using volatility and RSI
- ✅ Loadable stock graphs reflecting live data
- ✅ Breaking News Tab that displays articles in real time with predicted positive impact, with a
  ticker search filter
- ✅ Audible alert when a ticker newly enters Prime Setup
- ✅ Local integration API (`GET /screener`) for other tools/platforms to consume screener results
- ✅ 15-second best-effort IB enrichment and GUI/API snapshot cadence after cache warm-up

---

## 🔌 Data sources

This app tries **Interactive Brokers first** for discovery/screening, and **yfinance first** for
news — both free, no Finviz key needed:

- **Discovery/screening**: IB Gateway (or TWS), via `ib_async`. Requires IB Gateway installed,
  running, and logged in (paper trading account recommended; live works too — this app's IB usage
  is read-only, no order placement anywhere in the code). Falls back to the Finviz screener export
  only if IB never connects.
- **News/sentiment**: `yfinance`'s free `.news` property, fetched per-ticker, ahead of Finviz's bulk
  export (used automatically only if a real `FINVIZ_API_KEY` is set in `.env` — see "Optional: real
  Finviz Elite key" below). If yfinance itself returns nothing for a cycle (unofficial endpoint
  down/rate-limited), a third tier —
  NewsAPI.org via `core/newsapi_news_api.py` — kicks in automatically if a `NEWSAPI_KEY` is set (see
  "Optional: NewsAPI fallback" below). None of this needs manual switching; each tier is checked
  automatically in order.

**To use IB discovery:**
1. Install [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php) and log
   in with **your own** account — this connects to whatever Gateway is running on the configured
   host/port, so each person/team running this app uses their own login, not a shared one.
2. In Gateway: Configure → Settings → API → Settings — enable API access / "Allow connections from
   localhost only," and note the socket port shown (default `4002` paper, `4001` live).
3. If your port, host, or client ID differs from the defaults, set them in `.env` — no code changes
   needed: `IB_HOST` (default `127.0.0.1`), `IB_PORT` (default `4001`), `IB_CLIENT_ID` (default `7`,
   bump this if another API client is already connected to the same Gateway with that ID). Blank or
   malformed port/client-ID values safely fall back to those defaults.
4. Note: this account needs no special market-data or fundamentals subscriptions to run — the app
   requests live data (`reqMarketDataType(1)`, auto-falls-back to delayed per-symbol if a specific
   instrument isn't entitled) and free real-time price/Float fallbacks pick up the rest, so it
   still works end-to-end either way (see `PROJECT_NOTES.md` §8 for exactly what was verified
   live).

If IB Gateway isn't running, the app still works — it just falls back to whatever Finviz can supply
(nothing, unless a real key is configured) for discovery, while news still works via yfinance
regardless.

**Optional: real Finviz Elite key.** `FINVIZ_API_KEY` is blank by default (see `.env.example`) —
no key means Finviz is skipped and the app runs entirely on IB + yfinance, same as always. Two ways
to set it if you have real Elite credentials:
- **Manual (recommended for a one-off):** log into `elite.finviz.com`, copy your export API token
  from your account/Elite page, and put it in `.env`: `FINVIZ_API_KEY=your-token-here`.
- **Automatic:** `core/finviz_auth.py` logs in with `FINVIZ_USERNAME`/`FINVIZ_PASSWORD` (set those
  in `.env` instead) via a browser-fingerprint-impersonating HTTP client (`curl_cffi`, already a
  yfinance dependency — needed because Finviz blocks plain scripted requests), scrapes the token off
  a logged-in page, and writes `FINVIZ_API_KEY` into `.env` automatically. Run it by hand when you
  need a token: `python core/finviz_auth.py`. It's deliberately *not* run automatically on every app
  start — repeated automated logins against a real account risk tripping Finviz's own bot/lockout
  protections, so re-run it manually if the token ever needs refreshing.

**Optional: NewsAPI fallback.** yfinance needs no setup and is the default free news source; NewsAPI
is only an extra safety net for when yfinance itself comes back empty. To enable it, put a NewsAPI.org
key in a `.env` file at the project root (`ScreenerProject/.env`, gitignored — copy `.env.example` and
fill it in):

    NEWSAPI_KEY=your-key-here

`core/newsapi_news_api.py` loads this automatically (via `python-dotenv`, already in
`requirements.txt`) — no code changes or manual `export` needed. Without a `.env`/key present, this
tier just no-ops and the app behaves exactly as it did before (Finviz → yfinance only). Capped at 90
requests/day and cached 30 minutes per ticker, since the free tier's own ~24h article delay makes
faster polling pointless.

## 🔌 Integration API

A local, read-only REST API starts automatically with the app (`main.py`, background thread, port
`8000`) for other tools/platforms to consume screener results — no setup needed:

- `GET http://localhost:8000/screener` — the current Prime/Subprime results, in a typed JSON shape
  (`schema_version`, `ticker`, `price`, `float_shares`, `rel_volume`, `change_percent`, `short_float_percent`,
  `target_percent`, `stop_loss_percent`, `sentiment_label`, `sentiment_confidence`, `setup_tier`,
  `source`, `timestamp`). Missing/non-numeric fields are JSON `null`, not a placeholder string.
  `source` is `"ib"` or `"finviz"` depending on which discovery path produced that cycle's data.
- **Sentiment output is replaceable and optional.** The integration team is developing its own
  sentiment component. Set `INCLUDE_SENTIMENT_OUTPUT=false` in `.env` to omit `sentiment_label` and
  `sentiment_confidence` from local JSON, MongoDB, and the Vercel read API. This only changes the
  integration contract; the desktop app can continue using its built-in FinBERT display.
- `GET http://localhost:8000/health` — readiness/freshness check. Returns `200` with `status: "ok"`
  when the latest snapshot is valid and at most 60 seconds old, or `503` with
  `starting`/`unavailable`/`stale` otherwise.

An empty `[]` from `/screener` is valid and means the latest completed scan found no qualifying
Prime/Subprime stocks; use `/health` to distinguish that from a producer that has not started or
has gone stale. Every non-empty row carries `schema_version: 1`.

Field freshness is intentionally mixed: live price/borrow enrichment and snapshots target 15
seconds after warm-up; RSI/volume history is cached for one hour; float/short-float is cached for
24 hours; yfinance news is cached for 10 minutes (NewsAPI fallback: 30 minutes).

This just reads `data/screener_snapshot.json`, which the Screener tab overwrites every 15s refresh
— so the same data is available as a plain file if a consumer would rather not use HTTP at all.
Deliberately no auth/rate-limiting/HTTPS: this is a local dev tool, not a public API. See
`PROJECT_NOTES.md` §9 for the full design rationale.

**Optional: reach it from outside localhost.** Set `MONGODB_URI` in `.env` and each cycle's
snapshot also gets mirrored into MongoDB (`core/mongo_client.py`, no-op if unset). Pair that with
`../vercel-api/` (a separate small deployable app one level up) for a public URL serving the same
`/screener`/`/health` shape — see that folder's own README for setup. See `PROJECT_NOTES.md` §9a
for why this is a local-app-plus-cloud-read-API split rather than the whole app moving to the
cloud (the screener itself needs a persistent local IB Gateway connection Vercel can't provide).

## ⚠️ Common Troubleshooting Issues

- **Screener tab empty**: either IB Gateway isn't running/connected (check Configure → API →
  Settings in Gateway), or it is connected but no tickers matched this scan cycle (a valid empty
  result, not a bug) — see `PROJECT_NOTES.md` §8.
- **Breaking News tab empty**: shouldn't happen with a working internet connection, since yfinance
  needs no key — check for network access if it's persistently empty.
- **Optional ML/chart packages missing**: the live screener and API still start; sentiment becomes
  blank and the chart action becomes a no-op until `pip install -r requirements.txt` is completed.
- Finviz Elite is optional — if you have a real key, set `FINVIZ_API_KEY` in `.env` and it will be
  used automatically ahead of the free fallbacks above.


## 📦 Installation

1. Clone or download the repo  
2. Create virtual environment *(optional but recommended)*  
3. Install requirements:
    In your terminal run
        pip install -r requirements.txt
    - This app uses Tkinter for the GUI. Tkinter comes pre-installed with most Python distributions.
    If you're on Linux and it's missing, install it via:
        Debian/Ubuntu: sudo apt-get install python3-tk
        Fedora: sudo dnf install python3-tkinter
    - For live discovery via IB, also install and log into
      [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php) — see "Data
      sources" above. Optional: the app runs without it, just without live IB-sourced discovery.

- Tested on Python 3.10
- **First run only:** the sentiment model (`ProsusAI/finbert`) downloads from Hugging Face Hub the
  first time the app starts (~420MB) and is cached locally afterward — needs internet once, works
  offline after that.

## ▶️ Running the App

run file: main.py

No API keys required to run. For live IB-sourced discovery, have IB Gateway running and logged in
first (see "Data sources" above) — otherwise the app still runs, using yfinance for news and
whatever Finviz can supply (nothing, without a real key) for discovery.

## 📁 Project Structure

ScreenerProject/

├── core/
│   ├── filters.py              squeeze filter logic, prime/subprime scoring, shared target/stop-loss formula
│   ├── finviz_api.py           optional/opportunistic Finviz Elite screener + news fetchers, needs FINVIZ_API_KEY in .env
│   ├── finviz_auth.py          optional: auto-fetches FINVIZ_API_KEY via a real Finviz Elite login, run manually
│   ├── ib_api.py               IB scanner discovery + shortable-share enrichment (primary discovery source)
│   ├── finnhub_api.py          optional real-time price backup, needs FINNHUB_KEY in .env
│   ├── yfinance_news_api.py    free, keyless per-ticker news fetcher (primary news source)
│   ├── newsapi_news_api.py     optional third-tier news fallback, needs NEWSAPI_KEY in .env
│   └── sentiment.py            pretrained/fine-tuned FinBERT headline classifier (positive/neutral/negative)
├── controller/
│   └── controller.py           screener/news/sentiment orchestration; get_snapshot() for the API; Prime-entry alert
├── ui/
│   └── view.py                 Tkinter GUI; writes screener_snapshot.json each cycle; Breaking News ticker search
├── api_server.py                local FastAPI integration API (GET /screener, GET /health), see "Integration API" above
├── assets/
│   └── prime_alert.mp3          notification chime played on a new Prime-setup entry
├── tests/
│   ├── test_filters.py                    offline unit tests, mocked Finviz response, no live key needed
│   ├── test_yfinance_news_sentiment.py    manual smoke script, live network, no key needed
│   ├── test_newsapi_news_sentiment.py     manual smoke script, needs NEWSAPI_KEY in .env
│   ├── test_ib_api.py                     offline unit tests, no live Gateway needed
│   ├── test_sentiment_finbert.py          old vs. zero-shot vs. fine-tuned model comparison
│   ├── finetune_sentiment.py              fine-tunes FinBERT on labeled_data.csv, run manually
│   ├── evaluate_sentiment_outcomes.py     bonus: grades logged sentiment vs. real price outcomes
│   ├── audit_labeled_data.py              flags likely-mislabeled training rows, run manually
│   └── build_price_labeled_data.py        adds real, price-confirmed headlines via yfinance
├── model/
│   └── finbert_finetuned/       generated by finetune_sentiment.py; gitignored, local-only
├── data/
│   ├── labeled_data.csv         audited + expanded with real headlines, see PROJECT_NOTES.md §8e
│   ├── prime_log.csv
│   ├── screener_snapshot.json   mirrored snapshot backing the integration API, overwritten each cycle
│   ├── sentiment_outcomes.csv   generated by evaluate_sentiment_outcomes.py; not present until run
│   ├── sentiment_eval_log.csv   summary metrics, appended each test_sentiment_finbert.py run
│   ├── sentiment_eval_log.txt   full confusion matrices/reports, appended each run
│   └── label_audit_flags.csv    generated by audit_labeled_data.py; not present until run
├── main.py                      also starts the integration API server
├── requirements.txt
├── .env.example                 copy to .env; all keys optional (NEWSAPI_KEY, FINNHUB_KEY, FINVIZ_API_KEY/FINVIZ_USERNAME/FINVIZ_PASSWORD)
└── README.md


## ⚙️ Filter Logic

**Finviz path** (Prime = 4/4, Subprime = 3/4):

Price: $2–$20

Float: < 20M

Change: ≥ +10%

Relative Volume: ≥ 5.0

Short Float: ≥ 5%

**IB path** (Prime = 4/4, Subprime = 3/4) — same criteria as the Finviz path. IB itself still can't
supply Float/Short-Float without a paid fundamentals-data subscription this account doesn't have
(`reqFundamentalData` error 10358), but as of 2026-07-09 that gap is closed for free using
yfinance's `.info` endpoint instead (cached 24h — this data isn't more current than that anywhere,
since official short interest is only reported twice a month industry-wide). IB's own price/volume
ticks were **previously forced into delayed mode in code** (`reqMarketDataType(3)`) based on an
assumption that this account had no real-time entitlement at all — as of 2026-07-09, checked
directly in IB's Client Portal and found that's wrong: this account already carries a $0/"Fee
Waived" **US Real-Time Non Consolidated Streaming Quotes** entitlement (BATS/BYX/EDGX/EDGEA/IEX).
Fixed to request live data as the preferred type (`reqMarketDataType(1)`, which auto-falls-back to
delayed per-symbol if a specific instrument isn't entitled, so it's safe either way) — this account
should now get real-time ticks for most US equities at no cost, not the ~15-20 min delay. A
secondary free real-time source, `core/finnhub_api.py` (Finnhub's free tier), is wired in as a
last-resort fallback if IB's own tick is ever transiently unavailable, gated on an optional
`FINNHUB_KEY` in `.env` — demoted from primary to backup after real use showed its free-tier rate
limit (60 req/min) gets exhausted almost immediately at this app's actual scanner volume. See
`PROJECT_NOTES.md` §8 for the full rationale and implementation.


## 🧠 Sentiment Model
Uses FinBERT (`ProsusAI/finbert`) via Hugging Face `transformers` — a BERT model trained on real
financial text, then **fine-tuned on this app's own `labeled_data.csv`** (`tests/finetune_sentiment.py`,
linear-warmup LR schedule + class-weighted loss) for a further accuracy boost. Falls back to the
plain pretrained model automatically if no fine-tuned checkpoint is present (e.g. on a fresh clone —
the checkpoint is a local, gitignored ~420MB artifact, not committed). `classify_headlines()` also
supports an optional ensemble mode (blends in the zero-shot base model) - currently *off* by default
since the fine-tuned model alone measures better on the current data (see `PROJECT_NOTES.md` §8f/§8g
for why this is worth re-checking after any future change rather than assuming a fixed answer).

3-class output per headline: positive, neutral, or negative, each with a confidence score.

`labeled_data.csv` itself (823→1165 rows) has been audited (`tests/audit_labeled_data.py` flags
likely-mislabeled rows) and expanded twice with real headlines labeled by their actual subsequent
price move rather than guessed sentiment (`tests/build_price_labeled_data.py`, via `yfinance`,
including sourcing tickers from live day-gainers/day-losers screeners for higher yield) — see
`PROJECT_NOTES.md` §8e/§8g for the full methodology, including a real pitfall it ran into and fixed
(momentum-reversal noise on already-extended stocks) along the way.

Current best, measured on a held-out test split: accuracy 40% (old TF-IDF+RandomForest) → 54%
(FinBERT zero-shot) → 64% → 66% → **72.3%** (FinBERT fine-tuned, each step on more/better data and
training); macro F1 0.31→0.52→0.62→0.64→**0.71**. See `PROJECT_NOTES.md` §8d-§8g for the full
comparison, `tests/test_sentiment_finbert.py` to reproduce it, `tests/finetune_sentiment.py` to redo
the fine-tuning, and `data/sentiment_eval_log.csv`/`data/sentiment_eval_log.txt` for the persisted
numbers — every run appends a new row/entry rather than overwriting, so model quality is tracked
over time. The old model also couldn't distinguish neutral headlines from negative ones at all —
FinBERT fixes that by construction.

## 🗃️ Logging
Logs all 5/5 Prime setups to:

data/prime_log.csv
Ensures no duplicate ticker is logged more than once per day.

## 📈 Target / Stop-Loss Formula
Target = 0.7 × Volatility + 0.03 × (70 - RSI)

Stop = 0.3 × Volatility - 0.02 × (RSI - 50)

## 👨‍💻 Author
Built by William Gray as part of an internship/independent research project using Finviz Elite, Python, and machine learning.

# 📝 License
Free to use and modify.
