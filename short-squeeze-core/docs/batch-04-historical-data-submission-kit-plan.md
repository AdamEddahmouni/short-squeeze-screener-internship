# Batch 04 Preregistered Plan — Historical Data Submission Kit and Preflight

Task name: **Phase 3D Historical Data Submission Kit and Preflight Batch 04**

Branch: `batch/phase-3d-historical-data-submission-kit-04`
Created from Batch 03 final HEAD: `1c3b9329ea63fbfffe68281542bdf692170d50fc`
Schema version: unchanged at `1.0.0`.

This plan is frozen before implementation and committed on its own. Any necessary
deviation is documented here before the code that requires it lands.

---

## 1. Scope

Build an operator-facing **Historical Data Submission Kit** and an **offline
preflight workflow** on top of the completed Batch 03 `local_bar_intake` package.
The kit lets a technically capable user prepare a lawful, local historical
market-bar export that conforms to the Batch 03 intake contracts, and validate it
offline through preflight *before* any future real-case association, outcome
capture, Phase 3A evaluation, Phase 3B publication, or Phase 3E work.

This is an operator-preparation and validation batch only. It reuses the Batch 03
contracts, models, enums, reason codes, adapters, and normalization unchanged. It
does not redesign or replace them.

The batch performs steps 2–8 of the operator journey (place file, declare
provenance/semantics, validate raw bytes, validate manifest, validate mapping
profile, parse/normalize, review diagnostics) and produces a readiness status for
step 9. It never performs step 10 (case association) or step 11 (outcome capture).

## 2. Target operator

A technically capable user who can obtain a licensed or otherwise entitled
historical bar export, place files in folders, edit JSON, and run a CLI, but who
does not know the internal architecture. Documentation uses plain language while
preserving exact technical field names and constraints from Batch 03.

## 3. Kit directory layout (frozen)

Durable kit root:

```
operator-kits/historical-market-bars/
  README.md
  QUICKSTART.md
  EXPORT-CHECKLIST.md
  PROVIDER-AND-ENTITLEMENT-GUIDE.md
  TIMEZONE-INTERVAL-SESSION-GUIDE.md
  ADJUSTMENT-SEMANTICS-GUIDE.md
  SHA256-AND-BYTE-LENGTH-GUIDE.md
  FOLDER-PLACEMENT-GUIDE.md
  PREFLIGHT-GUIDE.md
  TROUBLESHOOTING.md
  FINAL-OPERATOR-CHECKLIST.md
  templates/
    intake-manifest.template.json
    column-mapping-profile.template.json
    case-association.template.json
  examples/
    synthetic-valid/
      intake-manifest.json
      column-mapping-profile.json
      raw/synthetic-bars.csv
      preflight-report.json
    synthetic-invalid/
      README.md
      invalid-scenario-index.json
```

Every file above is produced deterministically in-memory by a single generator so
repeated builds are byte-identical. The kit is fully regenerable; no file in it is
hand-maintained separately from the generator.

## 4. Template inventory (frozen)

Three JSON templates, each containing **every** field name from the corresponding
Batch 03 model, with placeholder values that are syntactically valid JSON,
unmistakably non-production (`<REPLACE: ...>` tokens or explicit nulls), non-secret,
non-identifying, and safe to commit. Templates are *fill-in* documents; they are
not required to pass model validation until the operator replaces placeholders.

- `intake-manifest.template.json` — all `IntakeManifest` fields (section 10 of the
  handoff), plus a `_field_guidance` block naming which fields the operator must
  replace and which have safe defaults.
- `column-mapping-profile.template.json` — all `ColumnMappingProfile` fields
  (section 11), plus `_field_guidance`.
- `case-association.template.json` — all `CaseAssociationMapping` fields, marked
  `NOT FOR USE IN BATCH 04 / FUTURE AUTHORIZED WORK ONLY`, populated with obvious
  `<PLACEHOLDER: ...>` values only. No Batch 01/02 or BIYA case IDs.

The leading-underscore guidance keys are template annotations only; the operator
removes them before validation. They are chosen so they never collide with real
model field names.

## 5. Example inventory (frozen)

One complete **synthetic valid** bundle, distinct from the Batch 03 fixture bundle
so the kit is self-contained:

- fictional provider `DEMO_FIXTURE_FEED`, fictional export product name;
- fictional symbol `ZZQ1`, fictional venue `DEMO_VENUE_X`;
- UTC timezone, fixed `FIVE_MINUTES` interval, six contiguous valid OHLC bars,
  nonnegative volume, explicit `RAW_UNADJUSTED` price/volume semantics,
  `SYNTHETIC_FIXTURE` authenticity, `INFRASTRUCTURE_FIXTURE` intended use,
  `HISTORICAL` time basis;
- deterministic dates/values, small enough to inspect by hand.

Recorded exactly for the example: SHA-256, byte length, normalized bar count,
deterministic bundle/artifact/profile IDs, and final preflight status
(`READY_FOR_FUTURE_ASSOCIATION`).

**Synthetic invalid** scenarios are documented as a deterministic index
(`invalid-scenario-index.json`) that reuses the Batch 03 normalization machinery to
record, for each scenario, the resulting status and reason codes plus the operator
remediation. Scenarios cover every barrier class listed in handoff section 13. No
unsafe input is auto-repaired.

## 6. Preflight behavior (frozen)

A pure, offline function `run_preflight(root, manifest, profile)` orchestrates the
Batch 03 primitives in this fixed order:

1. locate the local bundle root;
2. validate the manifest (Pydantic model validation on load);
3. inspect the raw artifact bytes;
4. verify SHA-256 and byte length (`validate_artifact_bytes`);
5. validate the mapping profile (Pydantic model validation on load);
6. parse and normalize supported bars (`normalize_bundle`);
7. produce deterministic diagnostics (`NormalizationDiagnostics`);
8. produce a deterministic readiness report (`PreflightReport`);
9. stop before case association;
10. never touch the network, credentials, or provider accounts.

A filesystem-free entry point `run_preflight_from_bytes(manifest, profile, content)`
backs the on-disk wrapper for deterministic testing.

## 7. Readiness statuses (frozen)

`PreflightStatus` enum:

- `READY_FOR_FUTURE_ASSOCIATION` — artifact ACCEPTED and normalization ACCEPTED.
- `NOT_READY_QUARANTINED` — normalization QUARANTINED (bars kept but some rows
  collapsed/quarantined; not clean).
- `NOT_READY_REJECTED` — artifact REJECTED or normalization REJECTED.

`READY_FOR_FUTURE_ASSOCIATION` means only that the local bundle passed the current
intake and normalization checks. It explicitly does **not** mean the data is
accurate, the license is legally sufficient, the bundle covers a particular
historical case, the outcome window is complete, Phase 3A can run, Phase 3B can
publish, or the project is predictively validated. This disclaimer is stated in the
report contract, the PREFLIGHT guide, and the completion report.

## 8. Preflight report contract (frozen)

`PreflightReport` (a frozen acquisition model, UUIDv5 deterministic id) contains at
least every field in handoff section 15:

```
schema_version, preflight_contract_version, bundle_id, artifact_id, profile_id,
status, reason_codes, artifact_sha256, artifact_byte_length, provider_name,
provider_product_or_export_name, user_entitlement_assertion, retrieval_time,
export_time, canonical_symbol, provider_symbol, market_or_venue, bar_interval,
event_timezone, timestamp_semantics, session_coverage, price_adjustment_semantics,
volume_adjustment_semantics, expected_start_time, expected_end_time,
observed_start_time, observed_end_time, normalized_bar_count, rejected_row_count,
quarantined_row_count, diagnostic_count, ready_for_case_association,
case_association_performed, outcome_capture_performed, phase_3a_records_created,
phase_3b_records_created, phase_3e_started
```

`ready_for_case_association` is true only when status is
`READY_FOR_FUTURE_ASSOCIATION`. The final five booleans
(`case_association_performed`, `outcome_capture_performed`,
`phase_3a_records_created`, `phase_3b_records_created`, `phase_3e_started`) are
constant `False` and are asserted so by tests. Unknown datetimes use explicit
null. No absolute local path enters identity or canonical output.

`preflight_contract_version = "phase_3d_submission_kit_preflight.v1"`.

## 9. Error and troubleshooting mapping (frozen)

`build_troubleshooting_index()` maps every major Batch 03 `IntakeReasonCode` to a
record with: `meaning`, `why_blocked` (block vs quarantine), `inspect`,
`may_change` (manifest/profile correction that is safe), `must_not_guess`,
`new_export_required`. It never advises bypassing source restrictions or editing
raw data to force acceptance; it distinguishes safe manifest/mapping corrections
from changing the raw artifact. Committed as `troubleshooting-index.json`; rendered
prose in `TROUBLESHOOTING.md`.

## 10. Documentation structure (frozen)

Operator guides (in the kit): README, QUICKSTART, EXPORT-CHECKLIST,
PROVIDER-AND-ENTITLEMENT, TIMEZONE-INTERVAL-SESSION, ADJUSTMENT-SEMANTICS,
SHA256-AND-BYTE-LENGTH, FOLDER-PLACEMENT, PREFLIGHT, TROUBLESHOOTING,
FINAL-OPERATOR-CHECKLIST.

Repository docs (`docs/`): this plan, plus architecture, preflight contract,
operator workflow, security/entitlement/credential boundary, determinism/fixture
report, test/verification report, completion report, and the Batch 05 handoff.

All guidance is aligned to actual Batch 03 behavior; no non-existent feature is
documented. Only enum options actually supported by Batch 03 are described.

## 11. CLI behavior (frozen)

New offline subcommands on the existing `squeeze-core` CLI, following existing
naming conventions:

- `submission-kit-generate --output-dir <dir>` — writes the full kit
  deterministically (default `operator-kits/historical-market-bars`).
- `historical-bar-hash --file <path>` — prints canonical JSON `{byte_length,
  sha256, file_name}`; offline; no absolute path in output.
- `historical-bar-preflight --root <dir> --manifest <f> --profile <f>
  [--output <f>]` — prints the `PreflightReport`; exit 0 when READY, 1 otherwise;
  optional `--output` writes canonical bytes.
- `historical-bar-preflight-report --root <dir> --manifest <f> --profile <f>
  --output <f>` — writes the deterministic report file (canonical bytes + LF).

No subcommand performs case association or accepts case-registry inputs.

## 12. Identity and determinism rules (frozen)

UUIDv5 identity (reusing `_FrozenAcquisitionModel`); canonical serialization via
`canonical_json_bytes`; stable field/file/fixture/diagnostic order; exact Decimal
strings; explicit nulls; UTF-8; LF endings; no NaN/infinity; no random IDs; no
wall-clock identity input; no machine-specific absolute paths in identity; no
credentials; no unordered iteration; no outcome data; no real case IDs in synthetic
templates. Generator, preflight, and report commands are run twice and compared
byte-for-byte; committed examples are regenerated and compared exactly; LF/CRLF
hash behavior is tested.

No new `IntakeReasonCode` members and no changes to any Batch 03 serialized bytes,
contract, or schema (adding enum members would alter the frozen Batch 03 intake
contract fixture — explicitly disallowed).

## 13. Fixture policy (frozen)

Committed canonical fixtures under `tests/fixtures/acquisition/batch04/`:

```
submission-kit-manifest.json
intake-manifest.template.json
column-mapping-profile.template.json
case-association.template.json
synthetic-valid-intake-manifest.json
synthetic-valid-column-mapping-profile.json
synthetic-valid-bars.csv
synthetic-valid-preflight-report.json
invalid-scenario-index.json
troubleshooting-index.json
operator-checklist.json
determinism-anchors.json
fixture-metadata.json
```

The user-facing kit under `operator-kits/` is regenerated exactly by the same
generator. Only synthetic data is committed; no real licensed market data.

## 14. Git-ignore policy (frozen)

The private intake root `intake/local-bars/` stays git-ignored (unchanged from
Batch 03). Regenerable build output stays under the already-ignored `build/`. The
`operator-kits/` kit and `tests/fixtures/acquisition/batch04/` fixtures are
committed (synthetic only).

## 15. Explicit non-goals

No acquisition, no downloading, no API calls, no provider integration, no account
creation, no credential handling, no scraping, no authentication/rate-limit/robots/
anti-bot/paywall bypass, no execution of archived helpers, no real market-data
ingestion (unless the user separately supplies and authorizes a specific file, and
even then no association/outcome), no real-case association, no BIYA/Batch 01/02
association, no outcome capture or calculation, no Phase 3A/3B records, no Phase 3C
expansion, no Phase 3E, no predictive validation, scoring, ranking, weighting,
threshold tuning, feature importance, ML, recommendations, alerts, buy/sell
language, entry/exit logic, P&L, backtesting, portfolio/paper/live trading, broker
orders, database persistence, auth systems, or GUI redesign. Schema stays `1.0.0`.

## 16. Stop conditions

Stop and report without improvising if: the starting branch/HEAD does not match;
the baseline cannot be reproduced (beyond the known cache warning); Batch 01/02/03
canonical artifacts are already modified; implementation would require network,
credentials, modifying archived evidence, real-case association, outcome access,
fabricating provider/entitlement semantics, changing prior serialized bytes or
schema, or beginning Phase 3E; or a required operator instruction would tell the
user to violate source restrictions. Routine implementation decisions are not stop
conditions.

## 17. Verification plan

1. verify starting branch/HEAD, status, remotes, tag, log; ✅ recorded in completion report;
2. verify archived parent + submodule topology unchanged;
3. reproduce `2,056 passed, 1 skipped, 0 failed` via JUnit XML;
4. record Batch 01/02/03 fixture digests;
5. create the branch from the exact Batch 03 HEAD;
6. preregister and commit this plan before implementation;
7. implement templates + operator kit;
8. implement preflight orchestration + report;
9. generate the kit twice, compare bytes;
10. run every new CLI twice, compare bytes;
11. regenerate committed fixtures exactly;
12. run focused Batch 04 tests;
13. run the acquisition package suite;
14. run isolation + documentation tests;
15. run the full suite with a fresh basetemp;
16. verify Batch 01–03 artifacts unchanged;
17. verify archived evidence unchanged;
18. verify no real case ID appears in generated examples;
19. verify no credentials/network/outcome logic/Phase 3A-3B records introduced;
20. produce the completion report;
21. create the actual Batch 05 fresh-session handoff;
22. commit final documentation; report the exact final HEAD; stop.
