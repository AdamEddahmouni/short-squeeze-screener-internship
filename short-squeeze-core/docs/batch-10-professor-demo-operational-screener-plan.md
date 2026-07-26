# Batch 10 — Professor-Demo Truthful Operational Screener (preregistration)

Branch `batch/professor-demo-operational-screener-10` from `663954ca14744653167b5f634b2ff0365ec25ed2`.

This is an **application / integration** batch. It is not Phase 3E, not predictive
validation, not optimization, and not trading. It adds a read-only view/controller layer
over artifacts and evaluators that already exist.

## 1. Architecture

New package `src/squeeze_core/app/` — a pure view/controller layer. It contains **no**
metric formula and **no** rule logic. Every outcome it shows is read from a frozen
canonical artifact or produced by the existing canonical evaluator.

| Module | Responsibility |
| --- | --- |
| `paths.py` | Locate the private artifact root; hard-block forward-window artifacts |
| `truth.py` | `DataMode`, `Freshness`, `FieldValue` — the display truth model |
| `reasons.py` | Code → human sentence mapping (unmapped codes shown verbatim) |
| `frozen.py` | MODE A loader over the Batch 08 freeze + Batch 09 preview |
| `providers.py` | Safe provider health probing |
| `live.py` | MODE B / MODE C read-only IBKR access (reuses `tools/ibkr_historical_export`) |
| `snapshot.py` | Assembles screener rows + symbol detail from the above |
| `export.py` | JSON + CSV research snapshot |
| `server.py` | stdlib `http.server` JSON API + static assets, localhost only |
| `static/` | `index.html`, `app.js`, `styles.css` — no framework, no CDN |

Launcher: `run_screener.ps1` at repository root, plus `python -m squeeze_core.app`.

UI choice: **local browser dashboard served by a stdlib Python HTTP server.** No new
dependency, no build step, one command. The repository already ships a static-JSON demo
(`apps/biya-validation-demo`), so this is the established practical path; Tkinter is not
restored.

## 2. Modes

| Mode | Label shown | Source | Requires network |
| --- | --- | --- | --- |
| A | `FROZEN RESEARCH — 2026-07-18` | Batch 08 freeze (13 real cases), Batch 09 preview | no |
| B | `LIVE` or `DELAYED` (never both) | local IB Gateway, read-only | yes (localhost socket) |
| C | Manual symbol, labelled as B | local IB Gateway, read-only | yes (localhost socket) |

Mode A is the primary demonstration and must work with every provider down. There is no
silent fallback: a mode is only ever entered by explicit user selection, and the active
mode is displayed permanently in the header.

No synthetic replay fixtures are shipped in this batch. `REPLAY` exists in the data-mode
enum but no code path produces it, so no synthetic value can ever be displayed.

## 3. Data boundaries

- Read-only. The app never writes into `intake/`, never mutates any canonical registry,
  and never re-runs the Batch 08 freeze.
- Forward-window artifacts (`*frozen-forward*`, `FROZEN_FORWARD_24H`) are hard-blocked by
  a path guard in `paths.py` that raises. Only `*-detection-context.csv` is readable.
- Outcome data is not read and not inferred. Outcome status is `INCOMPLETE` for all 13
  cases, sourced from the Batch 09 preview.
- The Batch 09 registry preview is displayed under the literal banner
  `REGISTRY REVISION PREVIEW — NOT CANONICALLY PUBLISHED`. The canonical Phase 3B
  registry is untouched pending the professor's governance decision.

## 4. Truthfulness rules

1. Missing is never zero. Absent values render `—` with an explicit status
   (`UNKNOWN`, `UNAVAILABLE`, `NOT COLLECTED`, `NOT CONFIGURED`, `STALE`).
2. `UNKNOWN` is never rendered as `PASS` and never as a neutral blank. The textual label
   is always present, independent of colour.
3. Every displayed cell carries `value, provider, event_time, received_time, freshness,
   data_mode, evidence_id, readiness, missing_reason` internally, and exposes them in the
   detail panel and the export.
4. Delayed data is labelled `DELAYED`. Historical data is labelled `HISTORICAL`. Neither
   is ever labelled `LIVE`.
5. The application's own refresh time is labelled *retrieved at* and is never presented as
   market-data event time.
6. No score, no ranking, no weight, no squeeze probability. No `PRIME` / `SUBPRIME` /
   `BUY` / `SELL` / `ENTRY` / `EXIT` / `TARGET` as an authoritative output.
7. Unmapped diagnostic codes are shown verbatim rather than suppressed.

## 5. Provider policy

Permitted: local IB Gateway on `127.0.0.1`, read-only, via the already-validated
`tools/ibkr_historical_export` session (contract details, historical bars, current time).

Forbidden and not implemented: any order method (`placeOrder`, `cancelOrder`,
`reqOpenOrders`, …), any account method (`reqAccountSummary`, `reqPositions`, …), the
archived Finviz TLS-impersonation helper, any archived authentication-bypass helper, any
scraping or access-control bypass. A test asserts the app package contains none of these
identifiers.

Providers that are not configured are reported `NOT CONFIGURED`, never `AVAILABLE`.
Availability is asserted only from a live probe result, never from the existence of code.

## 6. UI plan

Header: title, `RESEARCH TOOL — NOT A TRADING RECOMMENDATION`, active mode badge,
provider health strip. Left: screener table. Right: symbol detail with identity,
market data, short pressure, catalyst, the 25-rule table in canonical order, research
status summary, and a detection-context price chart with the frozen boundary drawn.
Buttons: Refresh, Export, Professor Mode.

## 7. Priorities

P0 (§5 of the handoff) is implemented first and completely. P1 is attempted after P0 is
green. P2 is not attempted.

## 8. Test plan

Meeting-critical assertions: 13 frozen symbols; 25 rules each; 325 rule-case pairs;
97 PASS / 20 FAIL / 208 UNKNOWN; the exact `PERCENTAGE_CHANGE_MINIMUM` 6-PASS/7-FAIL
split; `PREFLIGHT_REJECTED` surfaced; detection `UNEVALUABLE` ×13; outcome `INCOMPLETE`
×13; forward artifacts blocked; missing never zero; export JSON/CSV valid and
credential-free; no order/account identifiers; no ranking model; canonical registry,
Batch 05 raw, and Batch 08 freeze byte-unchanged. Plus an HTTP smoke test that walks the
meeting demo script end to end against a live server instance.

## 9. Definition of done

One command launches a localhost dashboard that demonstrates the §28 walkthrough with no
fabricated evidence, no fake live labels, no score, no orders, canonical registries
unchanged, prior artifacts intact, and the full suite green.
