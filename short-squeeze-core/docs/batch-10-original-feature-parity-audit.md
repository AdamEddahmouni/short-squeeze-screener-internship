# Batch 10 — Original Application Feature Parity Audit

Source audited, read-only:
`archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject`
(archived parent `0897562e05d75b812dd284de81dfafdfa1dea916`, nested
`6dbefd1a6b271bfc48106c4aa002f211735551cd`). Nothing in the archive was modified.

The original was a Tkinter desktop app that also started a FastAPI server on
`127.0.0.1:8000` in a daemon thread and served a second, browser-based UI from
`static/`. The Tkinter thread was the only producer; it wrote
`data/screener_snapshot.json` every 15 s and the web UI read that file.

Parity here means **parity of useful workflow**, not parity of unsupported claims.

## Classification

| Original feature | Where it lived | Classification | What Batch 10 does |
| --- | --- | --- | --- |
| One-command launch | `python main.py` | IMPLEMENT_TONIGHT | `.\run_screener.ps1` / `python -m apps.research_screener` |
| Browser dashboard | FastAPI + `static/` | IMPLEMENT_TONIGHT | stdlib HTTP server + `apps/research_screener/static/`, localhost only |
| Tkinter desktop UI | `ui/view.py::View` | REMOVE_AS_UNSUPPORTED | One UI, not two. The browser path is faster to make reliable and was already the richer of the two |
| Screener table | 33-col Treeview / 13-col web table | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | 17 columns, every cell carrying provenance and an explicit missing reason |
| Symbol rows / drilldown | `buildDetailGrid()` | IMPLEMENT_TONIGHT | Symbol detail panel with identity, market data, short pressure, catalyst, provenance |
| Candidate discovery | IB `ScannerSubscription` `TOP_PERC_GAIN`, Schwab `/movers`, Finviz export | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | Frozen Research cohort (13 real cases) + Manual Symbol mode. Automated discovery is DEFERRED — see below |
| Price | IB tick → Finnhub → last close | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | Frozen mode: `UNKNOWN` — absolute price levels are blocked by Batch 07. Current mode: last completed bar close with event time and freshness |
| Price change % | computed from `prev_close` | IMPLEMENT_TONIGHT | Frozen mode: the frozen canonical `PERCENTAGE_RETURN` record, displayed verbatim |
| Volume | not displayed | ALREADY_AVAILABLE | Still not displayed; volume semantics are unresolved |
| Relative volume | `last bar / mean(prior)`, defaulted to `0.0` | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | `UNKNOWN` with the Batch 07 volume-semantics reason. Never `0.0` |
| Float | yfinance `.info["floatShares"]` | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | `NOT COLLECTED` — no float provider is configured |
| Short float | `(shares_short / float) * 100` | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | `NOT COLLECTED`, 91 `UNKNOWN` rule outcomes explained |
| Short interest / shares short | yfinance | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | `NOT COLLECTED` |
| Days to cover | `shares_short / avg_volume` | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | `NOT COLLECTED` |
| Borrow fee / rebate | IB anonymous FTP `usa.txt` | DEFER | `NOT CONFIGURED`. In the archive this feed was timing out and every score was silently computed from 3 of 4 inputs |
| Borrow availability | IB tick 236 shortable shares | DEFER | `NOT CONFIGURED` |
| Schwab hard-to-borrow | Schwab `/quotes` `reference.htb*` | DEFER | Not implemented; would require brokerage OAuth credentials |
| News | Finviz → yfinance → NewsAPI | DEFER | `NOT CONFIGURED`, 65 `UNKNOWN` catalyst outcomes explained |
| Sentiment | FinBERT over matched headlines | REMOVE_AS_UNSUPPORTED | `NOT CONFIGURED`. No current research supports a sentiment field as evidence |
| Prime / Subprime tier | `classify_tier()`, score ≥70 & SF ≥5 | REMOVE_AS_UNSUPPORTED | Replaced by Research Evaluation / Research Detection / Evidence Coverage / Outcome. See below |
| Squeeze Score (0–100) | 4 weighted components, renormalised | REMOVE_AS_UNSUPPORTED | No score exists anywhere in the application |
| Squeeze Confirmed badge | relvol ≥5 & \|change\| ≥50 & momentum ≥0 | REMOVE_AS_UNSUPPORTED | Replaced by the 25-rule table with per-rule outcomes |
| TTM Squeeze / momentum / fired | `compute_ttm_squeeze()` | DEFER | Not a Phase 3A rule; no admissible input exists |
| Target % / Stop Loss % | `0.7·vol + 0.03·(70−rsi)` heuristic | REMOVE_AS_UNSUPPORTED | Removed. The project's own notes call it "a rough heuristic, not a validated model" |
| Corroboration score | Schwab re-scored via `score_setup` | REMOVE_AS_UNSUPPORTED | No score, so nothing to corroborate against |
| Quality flags | 16 literal flag strings | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | Superseded by per-field status + reason on every cell, and by per-rule blocking reason codes |
| Refresh (15 s auto) | `root.after` / `setInterval` | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | Explicit Refresh button. Auto-refresh is deliberately absent: frozen artifacts do not change, and silent background provider calls would obscure which data the reader is looking at |
| Charts | matplotlib 5d/30m; hand-rolled web SVG | IMPLEMENT_TONIGHT | Inline SVG of detection-context closes with the Detection Boundary drawn and no forward region |
| Persistence | JSON snapshots, 6 CSV logs, MongoDB mirror | DEFER | No application-owned database. Exports are written on demand |
| Export | none (JSON file / API / Mongo only) | IMPLEMENT_TONIGHT | Export button writing a timestamped JSON + CSV research snapshot |
| Provider integrations | IB, Schwab, Finviz, yfinance, Finnhub, NewsAPI, Mongo | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | Local IB Gateway only, read-only, via the already-validated Batch 05 session |
| Timestamps | mixed; several were cache-fetch times | IMPLEMENT_WITH_TRUTHFUL_REPLACEMENT | Every cell carries `event_time`, `received_time` and `freshness` separately. The application's retrieval time is labelled as such |
| Alerts | `prime_alert.mp3` on a new Prime ticker | REMOVE_AS_UNSUPPORTED | No alert. There is no Prime tier to alert on, and an alert on a research status would read as a signal |
| Status banner | `Live — updated <time>` etc. | IMPLEMENT_TONIGHT | Header mode badge + provider health strip + status line |
| Health endpoint | `GET /health` | ALREADY_AVAILABLE | `GET /api/health` with per-provider state and detail |
| Trading / orders | none present | ALREADY_AVAILABLE | Still none. Asserted by a source-level test |

## Deliberate exclusions

**`core/finviz_auth.py`** is excluded in full. `_login()` posts the account e-mail and
password to Finviz using `curl_cffi` with `impersonate="chrome"` — a forged Chrome TLS
fingerprint whose stated purpose is defeating bot detection — and `_find_auth_token()`
scrapes the account's export token out of page HTML, which `_write_token_to_env()` then
writes back into `.env`. That is access-control bypass and it is not carried forward. A
committed test asserts the strings `curl_cffi`, `impersonate`, `finviz_auth` and
`login_submit` appear nowhere in the application package.

**`core/schwab_auth.py`** and the Schwab token persistence path in `core/schwab_api.py`
are excluded: they obtain and store live brokerage OAuth credentials on disk.

**The archived `.env`, `data/schwab_tokens.json` and `logs/app.log`** contain real
credentials — including a plaintext account password and a Finviz auth token leaked into
a logged URL. None of it is read, copied or referenced. Those credentials should be
rotated independently of this project.

**Automated candidate discovery is deferred.** The original's IB scanner path is
technically available through the local gateway, but a discovered cohort is a research
population: admitting one tonight without a preregistered eligibility rule would create
exactly the selection-effect problem Batches 01–09 were built to avoid. Manual Symbol
mode gives the same operational reach without silently defining a cohort.

## Replacing the misleading labels

`PRIME`, `SUBPRIME`, `SQUEEZE CONFIRMED`, `Target`, `Stop Loss`, `Squeeze Score` and
`Corroboration Score` are not resurrected as authoritative outputs, and no original label
is displayed anywhere in the new application — so no
`ORIGINAL PLATFORM LABEL — NOT CURRENT RESEARCH CONCLUSION` caption is needed yet. If a
future batch displays them for historical comparison, that caption applies.

The modern statuses, all drawn from existing project enums:

| Field | Values | Source |
| --- | --- | --- |
| Phase 3A outcome | `PASS` / `FAIL` / `UNKNOWN` / `CONFLICTED` / `INSUFFICIENT_DATA` / `NOT_APPLICABLE` | `RuleOutcome` |
| Research Detection | `DETECTED` / `NOT_DETECTED` / `UNEVALUABLE` | `DetectionStatus` |
| Outcome | `COMPLETE` / `PARTIAL` / `UNAVAILABLE`, surfaced as `INCOMPLETE` for all 13 | `OutcomeCompleteness` |
| Evidence Coverage | `x / 25 rules supported` | count of `PASS` + `FAIL` |

## Silent-fabrication defects that are structurally impossible now

The audit found the original converted missing evidence into numbers in at least six
places: degraded RSI/volatility placeholders (`rsi=50.0`, `vol_w=0.0`) flowing into
displayed Target/Stop values; `rel_volume` defaulting to `0.0`; `_shortfloat_num`
defaulting to `0.0` and then being scored as a definite failure; `change_from_close()`
returning the string `'0'`; the Finviz path stamping `FloatAsOf = now()` on a value of
unknown vintage; and a `Float (M)` column holding raw share counts.

In Batch 10 a `FieldValue` with any status other than `KNOWN` raises if a value is
attached to it, and raises again if no reason is given. The defect class is closed at the
type level, not by convention.
