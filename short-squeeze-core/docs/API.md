# API

API version is `1.0.0`; integration schema is `batch14.integration.v1`. Responses
use an envelope containing `api_version`, `schema_version`, `mode`, `as_of`,
`data`, `status`, `missingness`, and `provenance`. Legacy top-level fields remain
where required for compatibility.

## Application routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Default Scanner UI |
| GET | `/advanced` | Advanced Research dashboard |
| GET | `/index.html` | Advanced Research (alias) |
| GET | `/research` | Advanced Research (alias) |

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness and provider status |
| GET | `/ready` | Mode-specific readiness |
| GET | `/api/health` | Provider health status |
| GET | `/api/providers` | Provider capabilities and health |
| GET | `/api/capabilities` | Provider capability matrix |
| GET | `/api/coverage` | Field coverage summary |
| GET | `/api/frozen/candidates` | Sanitized deterministic candidates |
| GET | `/api/frozen/candidate/<symbol>` | Frozen candidate detail |
| GET | `/api/current/candidates` | Current research candidates |
| GET | `/api/current/candidate/<symbol>` | Current candidate detail |
| GET | `/api/screener?mode=` | Main screener data (CURRENT or FROZEN_RESEARCH) |
| GET | `/api/symbol?symbol=` | Single symbol detail |
| POST | `/api/current/refresh` | Refresh due provider evidence |
| POST | `/api/refresh/all` | Refresh all providers for all tracked symbols |
| POST | `/api/discovery/refresh` | Refresh read-only discovery |
| GET | `/api/discovery/profiles` | Discovery profile listing |
| GET | `/api/methodologies` | Methodology definitions and comparison |
| GET | `/api/methodologies/<symbol>` | Symbol methodology projections |
| GET | `/api/news/status` | News orchestrator status |
| GET | `/api/news/symbol?symbol=` | News headlines for a symbol |
| GET | `/api/sentiment/status` | Sentiment analyzer status |
| GET | `/api/sentiment/symbol?symbol=` | Sentiment analysis for a symbol |
| POST | `/api/export` | Write a sanitized research export (JSON + CSV) |
| GET | `/api/v1/integration/manifest` | Machine-readable integration contract |
| GET | `/api/research-summary` | Historical research summary |
| GET | `/api/meta` | Application metadata (title, disclaimer, sort keys, modes) |
| POST | `/api/live/auto` | Toggle auto-refresh |
| POST | `/api/live/clear` | Clear current session |

There are no account, position, order, execution, or trading endpoints.
See `docs/openapi.json` for the static OpenAPI description.
