# Batch 15 Professional Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a provider-swappable, privacy-safe, verified integration-team release while preserving Batch 14 and all frozen research integrity.

**Architecture:** A central immutable configuration model feeds runtime and provider construction. An allowlisted release builder stages only reviewed product files, then a separate release audit and integration acceptance runner verify the staged directory and ZIP.

**Tech Stack:** Python 3.12, standard library, Pydantic 2.13.4, Requests 2.34.2, pytest 8.4.1, PowerShell, Docker, Railway.

## Global Constraints

- Preserve `.private/providers.env` and all current credential values unchanged.
- Do not start Phase 3E or add predictive validation, trading, order, or account access.
- Preserve API version `1.0.0`, integration schema `batch14.integration.v1`, frozen totals `97 PASS / 20 FAIL / 208 UNKNOWN`, and canonical registries.
- Leave `docs/phase-3c-complete-handoff.md` untouched and untracked.
- Do not modify archived repositories.
- New configuration and provider tests must be offline and deterministic.

---

### Task 1: Integrity checkpoint and repository map

**Files:**
- Create: `docs/superpowers/specs/2026-07-25-batch-15-professional-handoff-design.md`
- Create: `docs/superpowers/plans/2026-07-25-batch-15-professional-handoff-implementation-plan.md`

**Interfaces:**
- Consumes: Batch 14 Git checkpoint and existing private integrity CLIs.
- Produces: verified starting state and implementation boundaries.

- [x] Verify the exact branch, full HEAD, worktree, tag, logs, private Batch 05 artifacts, Phase 3A freeze, and archive references.
- [x] Create `batch/professional-build-and-handoff-15` from the exact Batch 14 HEAD.
- [ ] Record the tracked source, test, documentation, environment-read, and provider-construction surfaces.
- [ ] Commit the approved design and plan only after their self-review passes.

### Task 2: Central configuration and doctor

**Files:**
- Create: `apps/research_screener/config.py`
- Create: `.env.example`
- Modify: `apps/research_screener/__main__.py`
- Modify: `apps/research_screener/deployment.py`
- Modify: `apps/research_screener/live_providers.py`
- Modify: `apps/research_screener/providers.py`
- Test: `tests/app/test_batch15_config.py`

**Interfaces:**
- Produces: `ApplicationConfig.resolve(...)`, provider status records, `doctor_report()`, and `python -m apps.research_screener.config doctor [--json]`.

- [ ] Write failing tests proving argument > environment > explicit file > local private file > default precedence.
- [ ] Run the focused tests and confirm failures are caused by missing configuration behavior.
- [ ] Implement immutable typed configuration without reading private files at import time.
- [ ] Write failing tests for cloud/frozen/test isolation and provider `DISABLED` status.
- [ ] Implement environment-replaceable credentials and actual provider enable switches.
- [ ] Write failing doctor redaction/format/readiness tests, then implement text and JSON doctor output.
- [ ] Run the focused configuration suite and refactor only while green.

### Task 3: Privacy audit and professional terminology

**Files:**
- Create: `tools/release_audit.py`
- Create: `release-audit-allowlist.json`
- Modify: public app labels, messages, static assets, and release-eligible fixtures.
- Test: `tests/app/test_batch15_release_audit.py`

**Interfaces:**
- Produces: `audit_directory(path, allowlist_path=None, extra_patterns_path=None)` and a nonzero CLI exit on prohibited findings.

- [ ] Write failing tests for secret, email, phone, Windows path, Unix home path, academic marker, forbidden file, and safe-placeholder handling.
- [ ] Implement content scanning that reports categories, file-relative locations, and counts but never matched sensitive values.
- [ ] Write failing allowlist tests and implement narrow reviewed allowlist entries.
- [ ] Audit all tracked and untracked files, classify documents, and record counts without values.
- [ ] Neutralize production-facing labels while retaining backward-compatible machine IDs.

### Task 4: Release builder and metadata

**Files:**
- Create: `tools/build_handoff_release.py`
- Create: `release-files.json`
- Create: `RELEASE_MANIFEST.json`
- Create: `HANDOFF_README.md`
- Create: `INTEGRATION_CHECKLIST.md`
- Test: `tests/app/test_batch15_release_builder.py`

**Interfaces:**
- Produces: versioned staging directory, ZIP, per-file checksums, and deterministic release inventory.

- [ ] Write failing tests proving only allowlisted paths are copied and forbidden roots can never enter staging.
- [ ] Implement clean staging, manifest generation, audit enforcement, ZIP creation, and SHA-256 output.
- [ ] Write failing metadata and extracted-import smoke tests.
- [ ] Implement release metadata without absolute paths or secret-bearing environment values.
- [ ] Rebuild twice and confirm the staged inventory is stable apart from declared build metadata.

### Task 5: Integration acceptance and morning check

**Files:**
- Create: `tools/integration_acceptance.py`
- Create: `morning_check.ps1`
- Test: `tests/app/test_batch15_integration_acceptance.py`

**Interfaces:**
- Produces: `run_acceptance(base_url, mode)` with text/JSON serialization and stable check IDs.

- [ ] Write failing tests for health, readiness, versions, schema, providers, frozen totals, methodologies, manifest, export, and prohibited endpoint checks.
- [ ] Implement the URL acceptance runner with timeouts and sanitized failure messages.
- [ ] Add an offline frozen acceptance path for release validation.
- [ ] Implement the concise PowerShell orchestration without credential output.

### Task 6: Professional documentation and dependency inventory

**Files:**
- Rewrite: `README.md`
- Create: `docs/ARCHITECTURE.md`, `docs/CONFIGURATION.md`, `docs/API.md`, `docs/METHODOLOGIES.md`, `docs/PROVIDERS.md`, `docs/DEPLOYMENT.md`, `docs/TESTING.md`, `docs/SECURITY.md`, `docs/INTEGRATION.md`, `docs/LIMITATIONS.md`, `docs/CHANGELOG.md`
- Create: `docs/openapi.json`, `docs/release/privacy-and-handoff-audit.md`
- Create: `LICENSE_STATUS.md`, `THIRD_PARTY_NOTICES.md`, `DEPENDENCIES.md`
- Test: `tests/app/test_batch15_documentation.py`

**Interfaces:**
- Produces: organization-neutral install, configuration, API, security, deployment, methodology, and acceptance guidance.

- [ ] Write failing documentation presence, link, terminology, variable-name, and OpenAPI validation tests.
- [ ] Write the professional documentation using repository-relative examples and synthetic values.
- [ ] Inventory only installed runtime/build/test dependencies with versions, purposes, and licenses.
- [ ] Run the documentation and release audit tests.

### Task 7: Highest-value evidence and provider hardening

**Files:**
- Modify as proven necessary: `apps/research_screener/current_eval.py`, `live_providers.py`, `methodologies/evidence.py`, provider adapters, static UI, exports.
- Test: focused Batch 15 provider/evidence tests under `tests/app/`.

**Interfaces:**
- Produces: additive evidence fields with provenance and unchanged canonical semantics.

- [ ] Measure current candidate and canonical rule coverage.
- [ ] Write a failing end-to-end Float evidence regression if valid Float remains disconnected.
- [ ] Implement only the missing canonical-compatible Float link and confirm the rule result.
- [ ] Write timestamp/provenance tests for display news; map news to canonical evidence only where existing rule semantics permit.
- [ ] Document the exact Relative Volume and remaining short-pressure compatibility decisions.
- [ ] Add optional TTM or sentiment only if all P0 release gates are already green.
- [ ] Add sanitized provider timings, TTL use, last-good behavior, and log redaction only with focused failing tests.

### Task 8: Release and final verification

**Files:**
- Create generated ignored outputs under `dist/` and a writable external JUnit location.
- Create: `docs/batch-15-completion-report.md`, `docs/batch-16-fresh-session-handoff.md`

**Interfaces:**
- Produces: verified release directory, ZIP, checksums, acceptance result, final test totals, and handoff report.

- [ ] Run focused tests, then the full authoritative pytest command with fresh base/JUnit paths.
- [ ] Build and audit staging; create ZIP; extract into a new clean directory.
- [ ] Install in a fresh environment and run release-focused tests.
- [ ] Start extracted `FROZEN_DEMO`; verify HTTP health, readiness, dashboard, methodology, manifest, and export.
- [ ] Run integration acceptance and morning check.
- [ ] Deploy sanitized source to Railway only if authentication is available; otherwise record the exact blocker.
- [ ] Run final Git status, diff check, tracked/staged secret, privacy, class-material, and absolute-path scans.
- [ ] Verify private Batch 05, Phase 3A freeze, frozen totals, registries, archives, and Phase 3E stop state again.
- [ ] Commit cohesive changes, rerunning affected verification after any code change.
