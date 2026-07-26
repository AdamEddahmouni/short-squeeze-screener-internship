# Batch 14 Independent Prime Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved three-methodology comparison dashboard, evidence-gated
classification, integration API, deployment modes, and Railway delivery without changing
canonical Phase 3A or frozen research.

**Architecture:** A backend-only methodology package projects immutable current candidate
snapshots into versioned results. The existing session store remains authoritative.
Deployment/runtime concerns live in focused mode, frozen-demo, and API-envelope modules;
the frontend only renders server-calculated data.

**Tech Stack:** Python 3.12 standard library HTTP server, dataclasses/enums, vanilla
JavaScript/CSS/SVG, pytest 8.4.1, Docker, Railway config-as-code.

## Global Constraints

- Policy ID is exactly `adam_evidence_gated_prime.v1`.
- Missing values remain `None`; display-only evidence never contributes weight.
- Canonical Phase 3A, Phase 3B registry, Batch 05 raw, and Batch 08 freeze are read-only.
- Peer scoring remains `REFERENCE_DEFINITION_INCOMPLETE`.
- No external call occurs in normal tests.
- No probability, trading, order, account, outcome, or predictive-validity feature.
- `docs/phase-3c-complete-handoff.md` remains untracked and untouched.

---

### Task 1: Methodology contracts and normalizations

**Files:**
- Create: `apps/research_screener/methodologies/{__init__,enums,models,normalization,evidence}.py`
- Test: `tests/app/test_batch14_methodology_engine.py`

**Interfaces:**
- Produces: `EvidenceInput`, `DimensionResult`, `CoverageResult`, `MethodologyResult`,
  `linear()`, `inverse_linear()`, and `eligible()`.
- Missing scores serialize as explicit JSON `null`.

- [ ] Write failing tests asserting clamped normalization, immutable result serialization,
  explicit nulls, display-only exclusion, and the absence of prohibited output keys.
- [ ] Run
  `python -m pytest tests/app/test_batch14_methodology_engine.py -q`
  and confirm import/behavior failures.
- [ ] Implement the minimal contracts and helpers, including provenance, freshness,
  admissibility, conflict, and missing-reason fields.
- [ ] Rerun the focused file and confirm it passes.
- [ ] Commit as `feat: add independent methodology engine`.

### Task 2: Three profiles and comparison projection

**Files:**
- Create: `apps/research_screener/methodologies/{legacy,peer_reference,adam_v1,comparison,projection,serialization}.py`
- Modify: `apps/research_screener/session_state.py`
- Test: `tests/app/test_batch14_methodology_engine.py`

**Interfaces:**
- Produces: `evaluate_legacy(inputs)`, `describe_peer(inputs)`,
  `evaluate_adam(inputs)`, `compare_candidate(row)`, `project_candidates(rows, ...)`.
- Adam weights, critical domains, coverage bands, and classification precedence are copied
  exactly from the preregistration.

- [ ] Add failing tests for exact Legacy thresholds; missing daily change; no Short Float
  substitution; peer weights/thresholds/missing definitions; every Adam transform; 70%
  gate; critical domains; conflicts; all classifications; deterministic serialization.
- [ ] Add failing tests proving filtering/sorting do not mutate input order, missing sorts
  last in both directions, and `why_listed` persists.
- [ ] Implement the three profiles and immutable candidate projection.
- [ ] Rerun methodology and current-session focused tests.
- [ ] Commit as `feat: add methodology profiles and candidate projections`.

### Task 3: Versioned API, integration manifest, and trends

**Files:**
- Create: `apps/research_screener/{api_contract,deployment,trend}.py`
- Modify: `apps/research_screener/{server,snapshot,session_state}.py`
- Test: `tests/app/test_batch14_api_and_deployment.py`

**Interfaces:**
- Produces: versioned `envelope(data, mode, ...)`, `integration_manifest()`,
  `trend(values)`, runtime `DeploymentMode`.
- Adds path-style and query-style compatible aliases for current/frozen details.

- [ ] Write failing HTTP tests for `/health`, `/ready`, methodologies, current aliases,
  frozen path aliases, export alias, and `/api/v1/integration/manifest`.
- [ ] Write failing trend tests for `ASCENDING`, `DESCENDING`, `FLAT`, and
  `INSUFFICIENT_HISTORY` with first/latest/change/field.
- [ ] Implement stable envelopes and aliases while retaining old routes.
- [ ] Assert responses contain no secret-shaped keys or Windows paths.
- [ ] Commit as `feat: add comparison API and integration manifest`.

### Task 4: Frozen demo and deployment modes

**Files:**
- Create: `apps/research_screener/demo_data/frozen_research_v1.json`
- Create: `apps/research_screener/frozen_demo.py`
- Modify: `apps/research_screener/{__main__,server,paths,providers}.py`
- Test: `tests/app/test_batch14_api_and_deployment.py`

**Interfaces:**
- `LOCAL_FULL` binds `127.0.0.1:8787`.
- `CLOUD_PROVIDER_MODE` binds `0.0.0.0:$PORT`, skips `.private` and local IBKR.
- `FROZEN_DEMO` is network-free and returns 13 rows with 97/20/208 totals.

- [ ] Write failing tests for binding/PORT rules, cloud IBKR absence, no private-config
  load, demo totals, 25 ordered outcomes per row, and forbidden demo fields.
- [ ] Generate the sanitized aggregate from already public/sanitized frozen result
  material, excluding raw bars, IDs, paths, and outcomes.
- [ ] Implement mode selection and frozen source fallback.
- [ ] Run focused deployment and prior-integrity tests.
- [ ] Commit as `feat: add cloud modes and sanitized frozen demo`.

### Task 5: Comparison dashboard and research landscape

**Files:**
- Modify: `apps/research_screener/static/{index.html,app.js,styles.css}`
- Test: `tests/app/test_batch14_dashboard_contract.py`

**Interfaces:**
- Frontend consumes methodology API values without implementing formulas.
- SVG schema uses numeric Pressure/Ignition only; missing candidates are counted unplotted.

- [ ] Write failing static-contract tests for required labels/columns/filters, no scoring
  formulas in JavaScript, SVG axes, tooltip fields, plotted/unplotted counts, and disclaimers.
- [ ] Add the comparison tab/table, detail comparison rows, stable sort controls,
  classification/trend filters, and synchronized SVG scatter plot.
- [ ] Run dashboard, API, meeting-smoke, and truthfulness tests.
- [ ] Commit as `feat: add comparison dashboard and research landscape`.

### Task 6: Railway packaging and container verification

**Files:**
- Create: `Dockerfile`, `.dockerignore`, `railway.toml`
- Modify: `apps/research_screener/README.md`
- Test: `tests/app/test_batch14_packaging.py`

**Interfaces:**
- Container starts in `CLOUD_PROVIDER_MODE`, consumes `PORT`, and health-checks `/health`.
- Build context excludes `.private`, Git, pytest/JUnit output, private raw bars, caches.

- [ ] Write failing packaging tests for Docker/config fields and exclusion patterns.
- [ ] Implement a Python 3.12 non-root runtime image and Railway config-as-code.
- [ ] Build and run the image locally when Docker is available; otherwise record the exact
  unavailable capability and validate static/container configuration tests.
- [ ] Commit as `feat: add Railway deployment support`.

### Task 7: Documentation, local/cloud smoke, and Railway deployment

**Files:**
- Create/update all Batch 14, comparison, integration, professor, completion, and Batch 15
  documents required by the approved request.

- [ ] Launch local mode and verify frozen/current/methodology/export endpoints.
- [ ] Launch cloud mode on an explicit test `PORT`; verify demo, health/readiness, IBKR
  unavailable, no private path, export, and response timings.
- [ ] Audit and, only if needed, run the existing legitimate Finviz refresh command without
  printing secrets.
- [ ] Inspect Railway CLI authentication. Deploy and smoke-test if authorized; otherwise
  record the single exact login or project-selection action.
- [ ] Write the integration handoff/API contract and operational reports from observed
  results only.
- [ ] Commit as `docs: add Batch 14 integration and deployment handoff`.

### Task 8: Final verification and completion

**Files:**
- Update: `docs/batch-14-test-and-verification-report.md`
- Update: `docs/batch-14-completion-report.md`
- Update: `docs/batch-15-fresh-session-handoff.md`

- [ ] Run focused Batch 14 and integrity suites.
- [ ] Verify Batch 05 and Batch 08 at 26 artifacts/0 mismatches; archives and registry
  unchanged; frozen totals 97/20/208.
- [ ] Run one final full suite with `-p no:cacheprovider`, fresh pre-created `--basetemp`,
  and JUnit XML; parse totals from XML.
- [ ] Run `git diff --check`, staged-secret scan, prohibited-capability scan, and verify the
  protected untracked file remains untracked.
- [ ] Commit reports as `chore: finalize Batch 14`.
- [ ] Report the exact Phase 3E stop statement and one next task.

