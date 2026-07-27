# Continuous Evidence Collectors

Background collectors run alongside the live screener auto-refresh loop. They harvest **lawful supplemental evidence** (public FINRA files, SEC/RSS, configured REST APIs) and merge it into row cells through the same `FieldValue` provenance model.

## Policy

| Tier | Sources | Default |
|------|---------|---------|
| A | FINRA published SI, FINRA daily short volume, RSS/Atom news, SEC RSS, API keys (Polygon, Alpha Vantage) | On when `*_ENABLED` and credentials exist |
| B | yfinance (library only, no HTML scrape) | `YFINANCE_COLLECTOR_ENABLED=false` |
| C | Yahoo/Finviz HTML scrape, Stooq, login automation | **Not implemented** |

Social (Reddit, Stocktwits) uses **official OAuth/API tokens only**.

Collector-sourced cells are tagged `research_admissibility=RESEARCH_INADMISSIBLE` except FINRA published short interest normalized through `squeeze_core.adapters.finra` (`RESEARCH_ADMISSIBLE`).

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `COLLECTORS_ENABLED` | `true` | Master switch |
| `COLLECTOR_TICK_SECONDS` | `30` | Scheduler wake interval |
| `COLLECTOR_MAX_SYMBOLS_PER_TICK` | `10` | Batch size per tick |
| `COLLECTOR_MAX_REQUESTS_PER_MINUTE` | `60` | Global HTTP cap |
| `COLLECTOR_ORDER` | see `config.py` | Collector run order |
| `COLLECTOR_OVERRIDE_POLICY` | `never` | Set `display_fallback` to fill `NOT_CONFIGURED` only |
| `FINRA_SI_COLLECTOR_ENABLED` | `true` | Published short interest file |
| `FINRA_SI_DATA_URL` | — | Optional live FINRA file URL |
| `FINRA_SI_FIXTURE_PATH` | test fixture if present | Local file for dev/CI |
| `FINRA_DAILY_VOLUME_COLLECTOR_ENABLED` | `true` | Reg SHO daily file |
| `RSS_NEWS_ENABLED` | `true` | Google News RSS per symbol |
| `SEC_RSS_COLLECTOR_ENABLED` | `true` | SEC company Atom feed |
| `YFINANCE_COLLECTOR_ENABLED` | `false` | Opt-in display-only |
| `POLYGON_API_KEY` / `POLYGON_COLLECTOR_ENABLED` | off | Quote stub |
| `ALPHA_VANTAGE_API_KEY` / `ALPHA_VANTAGE_COLLECTOR_ENABLED` | off | Quote stub |
| `REDDIT_CLIENT_ID`, `REDDIT_SECRET`, `REDDIT_COLLECTOR_ENABLED` | off | Mention counts |
| `STOCKTWITS_ACCESS_TOKEN`, `STOCKTWITS_COLLECTOR_ENABLED` | off | Mention counts |
| `COLLECTOR_CACHE_ENABLED` | `true` | JSONL under `data/collector_cache/` |

## HTTP API

- `GET /api/collectors/status` — scheduler health, configured collectors, last tick
- `GET /api/collectors/symbol?symbol=GME` — debug snapshot from the evidence store

## Architecture

- Package: `apps/research_screener/collectors/`
- Scheduler prioritizes symbols with the worst `missing_evidence_buckets` on the current 50-ticker screen
- RSS/SEC headlines register into `NewsOrchestrator.register_external_headlines` (deduped by headline hash)
- Merge rules live in `collectors/merge.py`; KNOWN IBKR/Finviz cells are never overwritten unless override policy allows `NOT_CONFIGURED` fallback only

## Operations

Collectors start with bootstrap auto-refresh (`python -m apps.research_screener`). They stop when auto-refresh stops or the session resets.

CI should set `COLLECTORS_ENABLED=false` or rely on fixtures (`FINRA_SI_FIXTURE_PATH`) with network collectors disabled.
