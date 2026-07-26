# Architecture

## Application surfaces

The application serves two distinct interfaces from a single backend:

- **Scanner** (`/`): Default user experience. Clean financial-terminal table
  with symbol, price, change %, pressure, ignition, evidence coverage,
  classification, news, and sentiment. Compact filters and sortable columns.
  Click-to-expand detail drawer with headlines, sentiment summary, methodology
  comparison, and missing evidence.
- **Advanced Research** (`/advanced`, `/index.html`, `/research`): Full
  developer/research dashboard with 25 canonical Phase 3A rules, provider
  diagnostics, methodology comparison landscape, frozen research, integration
  manifest, and deployment information.

Both interfaces use the same backend API and methodology engine. No
methodology is duplicated.

## Runtime

`apps/research_screener` is a Python HTTP application with static HTML, CSS, and
JavaScript. `server.py` exposes read-only JSON endpoints and serves both
interfaces. `session_state.py` coordinates discovery, current evidence, provider
refresh, and methodology projection.

## Configuration boundary

`config.py` resolves immutable application and provider settings. Entry points
choose whether a local private file is eligible; library imports never load it.
Provider construction consumes the resolved configuration, so replacing or
disabling credentials does not require code changes.

## Provider boundary

Provider adapters normalize data into `FieldValue` objects containing value, unit,
provider, event time, receipt time, freshness, data mode, evidence ID, and
readiness. Missing, disabled, unavailable, and conflicted states remain distinct.
Independent calls never substitute a current value for unavailable historical
evidence.

### Provider refresh order

Per-symbol refresh fires in a round-robin slice respecting IBKR pacing limits
(60 requests per 10-minute rolling window, 3 symbols per cycle at 30s cadence).

External providers (Finviz Elite, NewsAPI, Finnhub, SEC EDGAR, Borrow Fee)
refresh concurrently alongside the per-symbol cycle. Provider caches respect
individual TTLs (300-900s depending on provider).

## Evidence projection pipeline

```
Provider data → session_state fields → evidence_from_row() →
EvidenceInputs → evaluate_adam() → Pressure / Ignition / Classification
```

The methodology evaluation (`adam_v1.py`) is called from `project_candidate()`
in the session row builder. It receives EvidenceInputs derived from live
provider fields with research admissibility gating. The result (pressure,
ignition, classification, coverage) is attached to each row and consumed by
both the Scanner and Advanced Research interfaces.

## Methodology boundary

The legacy, peer-reference, and Evidence-Gated Prime implementations live under
`methodologies/`. Canonical Phase 3A evaluation remains in `squeeze_core`.
Projection code is additive: it does not mutate the canonical registry or frozen
artifacts.

The verified Phase 3D acquisition packages remain the point-in-time evidence
foundation used by the canonical pipeline. They are preserved for integrity and
do not initiate Phase 3E.

## Metrics

Bar acceleration (`src/squeeze_core/metrics/bar_acceleration.py`) computes the
excess return of the most recent completed bar relative to the trimmed mean of
preceding bar returns. Catalyst age is derived from the most recent news
headline or SEC filing timestamp, whichever is newer.

## Release boundary

`release-files.json` is the distribution allowlist.
`tools/build_handoff_release.py` copies only those files into a new staging
directory, writes metadata and checksums, runs `tools/release_audit.py`, and then
creates the ZIP. Private files and Git history are outside this boundary.

The release builder auto-detects the project version from `pyproject.toml`.
The `--version` flag is available for overrides but defaults to the authoritative
project version.
