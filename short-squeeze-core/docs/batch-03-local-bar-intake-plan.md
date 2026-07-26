# Batch 03 — Local Historical Market-Bar Intake — Preregistered Plan

Status: **PREREGISTERED** (frozen before implementation)
Task: Phase 3D Local Historical Market-Bar Intake Batch 03
Branch: `batch/phase-3d-local-historical-bar-intake-03`
Starting branch: `batch/phase-3d-outcome-acquisition-02`
Starting HEAD: `06e3a97039a04b7247350bd57ed5f801998fe97b`

This plan is committed **before** any workflow implementation. It freezes the scope,
contracts, schemas, policies, non-goals, stop conditions, and verification plan for
Batch 03. Any necessary deviation is documented in the completion report before it is
implemented; the scope is not silently broadened.

---

## 1. Purpose and scope

Batch 03 is an **infrastructure** batch. It implements a deterministic, vendor-neutral,
fully offline workflow that lets the user place historical market-bar exports — obtained
from a source they are independently entitled to use — into a local intake location, and
then validates, normalizes, and summarizes those bars into deterministic canonical
records with preserved provenance.

Batch 03 builds intake, validation, normalization, provenance, determinism, and offline
handoff infrastructure. It **does not** acquire market data, access credentials, calculate
outcomes for the 13 frozen cases, promote cases into a complete Phase 3B dataset, or begin
Phase 3E.

The result makes a later, separately authorized curation batch possible without weakening
any evidence, leakage, or determinism rule.

### In scope (items 1–5 and a safe explicit mapping contract for item 6)

1. Raw local source artifact (bytes preserved, never modified).
2. User-supplied intake declaration (manifest).
3. Artifact validation (SHA-256 + byte length).
4. Parsing profile (explicit column-mapping profile).
5. Normalized canonical bars (deterministic).
6. A **non-executing** case-association mapping contract (structure + reference validation only).

### Out of scope (forbidden this batch)

7. Future outcome capture.
8. Future Phase 3B publication.

No outcome value may enter intake identity, artifact identity, provider identity,
mapping-profile identity, case selection, case inclusion, boundary selection, Phase 3A
identity, or any pre-outcome record.

---

## 2. Accepted input-bundle structure

```text
<private-intake-root>/                     # gitignored; never committed with real data
  <bundle-id>/
    intake-manifest.json                   # user-supplied declaration (canonical fields)
    raw/
      <original-export-file>               # bytes preserved exactly
    profiles/
      <column-mapping-profile.json>        # explicit parsing profile (CSV)
```

- The private intake root for real user data is `intake/local-bars/` and is added to
  `.gitignore`. Real licensed data is never committed unless the user later gives explicit
  authorization for the exact files.
- Tests and committed fixtures use only **synthetic** bundles under
  `tests/fixtures/acquisition/batch03/` with unmistakably dummy provider names and symbols.

---

## 3. Required manifest metadata (frozen field set)

`intake-manifest.json` carries explicit, canonical fields (explicit `null` required for
unknowns; unknown semantics normally block normalization):

```text
schema_version                 intake_contract_version        bundle_id
provider_name                  provider_product_or_export_name user_entitlement_assertion
license_or_terms_reference     retrieval_time                 export_time
artifact_relative_path         artifact_sha256                artifact_byte_length
artifact_media_type            artifact_format                provider_symbol
canonical_symbol               market_or_venue                bar_interval
event_timezone                 timestamp_semantics            session_coverage
price_adjustment_semantics     volume_adjustment_semantics    corporate_action_handling
expected_start_time            expected_end_time              column_mapping_profile_id
notes
```

Rules:

- No absolute path may enter any deterministic identity. Absolute paths may appear only in
  non-identity operational diagnostics when strictly necessary.
- `retrieval_time`, `export_time`, and bar event times are separate concepts and are kept
  separate throughout.
- `user_entitlement_assertion` is provenance recorded from the user, **not** a legal
  determination by the software.
- `notes` never affects deterministic identity.

---

## 4. Supported file formats

- **CSV / delimited text** — one complete reference adapter (required), driven by an explicit
  column-mapping profile. The adapter does not assume any single provider's column names.
- A **canonical JSON adapter** is out of scope for this batch (may be added later); it is not
  built here so it cannot delay or destabilize the required CSV workflow.
- No permanent provider integrations are built.

### Column-mapping profile declares

```text
delimiter          encoding          has_header
timestamp_column | date_column + time_column
timestamp_format   timezone_interpretation
open/high/low/close/volume column mapping
optional trade_count / vwap / currency column mapping
decimal_separator  thousands_separator_policy  null_tokens
sort_expectation   duplicate_policy
```

---

## 5. Canonical normalized market-bar schema

Each normalized bar (`CanonicalMarketBar`) carries at least:

```text
canonical_symbol  provider_symbol  market_or_venue  interval
event_start_time  event_end_time   event_timezone   session
open  high  low  close  volume  trade_count  vwap  currency
price_adjustment_semantics  volume_adjustment_semantics
source_artifact_id  source_row_number  source_record_id
```

Numeric rules:

- Deterministic decimal handling consistent with the repository (`Decimal`, serialized via the
  canonical JSON encoder). No binary-float drift, no NaN, no ±infinity, no locale-dependent
  parsing, no thousands separators unless explicitly declared by the profile, exact decimal
  strings in canonical serialized outputs.

Bar-integrity validation (never inferred, never repaired):

```text
high >= max(open, close, low)
low  <= min(open, close, high)
volume >= 0 when present
trade_count >= 0 when present
event_end_time > event_start_time
```

Missing OHLCV values are never inferred.

---

## 6. Validation, rejection, and quarantine policy

Deterministic statuses: `ACCEPTED`, `QUARANTINED`, `REJECTED` (bundle-level); per-row
`NORMALIZED`, `QUARANTINED`, `REJECTED`. Reason codes (enum `IntakeReasonCode`) block,
reject, or quarantine at least:

artifact missing; byte-length mismatch; SHA-256 mismatch; unsupported encoding; unsupported
format; malformed manifest; manifest schema mismatch; unknown timezone; ambiguous timezone;
missing timestamp semantics; missing interval; unsupported interval; event time outside
declared coverage; mixed intervals without declaration; missing adjustment semantics;
unsupported/contradictory adjustment semantics; symbol mismatch; market/venue mismatch;
malformed decimal; NaN/infinity; negative volume; negative trade count; invalid OHLC
relationship; duplicate timestamps; conflicting duplicate bars; overlapping bars;
non-monotonic order when the policy disallows it; coverage gaps when the policy requires
continuity; current values represented as historical; synthetic values represented as
historical; absolute path entering identity; credential-like values in fixtures; case
association attempted without an explicit mapping declaration.

Missing or ambiguous evidence stays missing or ambiguous — bars are never "repaired" by
guessing.

### Preregistered safe normalizations

- **Stable row sort**: when the profile's `sort_expectation` is `STABLE_SORT_BY_EVENT_START`,
  rows are stably sorted by `(event_start_time, source_row_number)`. `source_row_number` (the
  1-based line index in the raw artifact) is always preserved so provenance survives sorting.
- When `sort_expectation` is `REQUIRE_PRESORTED`, non-monotonic input is rejected
  (`NON_MONOTONIC_ORDER`) rather than reordered.

### Duplicate policy

- `duplicate_policy = COLLAPSE_IDENTICAL_REJECT_CONFLICTING` (default): byte-identical
  duplicate rows (same normalized content) collapse to one canonical bar with a diagnostic;
  two rows sharing an `event_start_time` but differing in any canonical field are a
  **conflicting duplicate** and reject the bundle (`CONFLICTING_DUPLICATE_BAR`).

### Continuity policy

- `session_coverage` declares expected continuity. `REQUIRE_CONTINUOUS` fixed-interval
  coverage rejects gaps (`COVERAGE_GAP`); `ALLOW_GAPS` permits them.

---

## 7. Deterministic identity policy

- UUIDv5 via the existing `deterministic_acquisition_id` (namespace-scoped canonical JSON).
- Canonical serialization, stable field order, stable artifact order, stable row order,
  stable diagnostic order, exact Decimal strings, explicit nulls, UTF-8, LF line endings.
- No NaN/infinity, no random IDs, no wall-clock in identity, no machine-specific absolute
  paths in identity, no credentials, no unordered iteration, no outcome data in pre-outcome
  identity.
- All generators, CLIs, and reports are run twice and compared byte-for-byte.
- Windows/Git line-ending behaviour is checked before committing fixtures (`.gitattributes`
  already enforces `eol=lf`; `*.jsonl` is `eol=lf`). The Batch 01 CRLF/hash defect is not
  repeated.

---

## 8. Timezone, session, and adjustment rules

- Timezone resolution reuses the existing market-bar timestamp parser
  (`squeeze_core.adapters.market_bars.parsing`), which already distinguishes unknown,
  ambiguous, and nonexistent local times. Unknown/ambiguous timezones block normalization.
- Sessions reuse `BarSession`; intervals reuse `BarInterval` from
  `squeeze_core.adapters.market_bars.semantics`.
- Price/volume adjustment semantics are explicit enums; `UNKNOWN` blocks normalization.
  Contradictory declarations (e.g. `ADJUSTED` price with `RAW`-only corporate-action handling
  that is declared incompatible) are rejected.

---

## 9. Case-association contract (non-executing this batch)

A deterministic `CaseAssociationMapping` requires explicit declarations:

```text
case_id  canonical_symbol  frozen_detection_boundary_id
requested_window_start  requested_window_end
required_interval  required_session_coverage  bundle_id
```

For Batch 03 the validator:

- validates mapping structure;
- verifies referenced `case_id`s and `frozen_detection_boundary_id`s exist in a
  caller-supplied known-reference set (so the example stays self-contained);
- verifies the bundle symbol and declared coverage are compatible;
- **does not** compute outcomes, open the outcome window, create Phase 3A requests/results,
  alter Batch 01/02 case records, or promote any candidate.

A mapping record is preparation for future authorized work, not evidence that the requested
window is complete.

---

## 10. Required implementation surface

```text
src/squeeze_core/acquisition/local_bar_intake/    # cohesive package
  __init__.py  contract.py  semantics.py  models.py
  artifact_validation.py  csv_adapter.py  normalization.py  case_association.py
src/squeeze_core/acquisition/batch03.py           # deterministic document builder
scripts/generate_batch03_local_bar_intake_outputs.py
```

CLI subcommands (offline; never network) added to `squeeze_core.__main__`:

1. `intake-validate-bundle` — validate an intake bundle (manifest + artifact).
2. `intake-inspect-artifact` — artifact metadata + hashes.
3. `intake-normalize-bars` — validate and normalize bars.
4. `intake-summary` — deterministic intake summary.
5. `intake-validate-case-association` — validate a future case-association mapping.

Follows the existing acquisition CLI style.

---

## 11. Fixture policy

- Synthetic-only, unmistakably synthetic, unrelated dummy provider names and symbols
  (e.g. provider `DEMO_HISTDATA_EXPORT`, symbols `ZZAA`, `ZZBB`).
- Never published as historical evidence or included in empirical estimates.
- Committed canonical outputs live under `tests/fixtures/acquisition/batch03/`; build outputs
  go to the gitignored `build/acquisition/batch-03/`.

Required generated outputs (canonical examples):

```text
intake-contract.json            valid-intake-manifest.json     column-mapping-profile.json
raw-artifact-manifest.json      artifact-validation.json       normalized-bars.jsonl
normalized-bars.csv             normalization-diagnostics.json intake-summary.json
case-association-example.json   case-association-validation.json rejected-intake-examples.json
determinism-anchors.json
```

---

## 12. Explicit non-goals

Public-source searching; network fetching; provider API calls; account creation; credential
access; scraping; permanent provider integrations; database persistence; authentication;
actual historical data ingestion (unless the user independently supplies a file during this
task and explicitly authorizes its use); outcome calculation; Phase 3A request/result
generation; Phase 3B labels or candidate promotion; expanded Phase 3C analysis; Phase 3E;
predictive validation; threshold tuning; scoring; ranking; feature importance; ML;
recommendations; alerts; entry/exit logic; buy/sell language; P&L; backtesting; portfolio
simulation; paper/live trading; broker orders; GUI redesign. Schema version stays `1.0.0`.

---

## 13. Stop conditions

Stop and report without improvising if: the branch is not
`batch/phase-3d-outcome-acquisition-02`; HEAD does not begin `06e3a97`; the baseline cannot
be reproduced (beyond the known cache warning); Batch 01/02 canonical artifacts are already
modified; the task would require network/credentials, modifying archived evidence,
fabricating bars/semantics, changing prior serialized bytes or schema, a genuine legal /
source-entitlement determination by the software, or beginning Phase 3E or another forbidden
direction. Routine implementation decisions are resolved conservatively from existing code
and documented policy.

---

## 14. Verification plan

1. Verify branch, full HEAD, status, remotes, tag, archived topology (done pre-plan).
2. Reproduce `1,993 passed, 1 skipped, 0 failed`.
3. Record Batch 01/02 fixture digests before any change.
4. Create the branch; preregister and commit this plan.
5. Implement contracts, validation/normalization, case-association boundary.
6. Generate fixtures twice; compare bytes.
7. Run focused Batch 03 tests.
8. Run the acquisition package suite and Phase 3 compatibility/isolation suites.
9. Run all new CLIs twice; compare bytes.
10. Regenerate committed fixtures; compare exactly.
11. Run the full suite with a fresh `--basetemp`.
12. Verify all prior anchors and serialized bytes are unchanged; Batch 01/02 digests match.
13. Verify archived repositories unchanged and clean.
14. Produce the completion report and fresh-session handoff; commit docs; report final HEAD.
