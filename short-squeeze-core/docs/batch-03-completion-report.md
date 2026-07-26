# Batch 03 — Completion Report

**Decision/status:** Complete. A deterministic, offline, vendor-neutral local
historical market-bar intake workflow is implemented, tested, and documented. No
market data was acquired, no outcome was computed, no Phase 3A/3B record was
created, no candidate was promoted, and **Phase 3E was not started**.

## Branches and HEADs

- Starting branch: `batch/phase-3d-outcome-acquisition-02`
- Starting HEAD: `06e3a97039a04b7247350bd57ed5f801998fe97b`
- New branch: `batch/phase-3d-local-historical-bar-intake-03`
- Final HEAD: the finalize documentation commit on the new branch (resolve with
  `git rev-parse HEAD`; the full hash is stated in the session closing report).

## Commit list

| hash | subject |
|---|---|
| `82a4bbb10e1748d291ad2e0ce5b897f277c7ed55` | docs: preregister local historical bar intake batch 03 |
| `9bf0e85a54b83bc6e15784e745c0cff0ffce970e` | feat: add deterministic offline local bar intake package |
| `b74dc0c73d6b934fdc953127f821d9f26bd4aff2` | feat: add offline intake CLI subcommands |
| `c4ceb37e71bd35beafb527651ffd266659ee4ed0` | feat: add batch 03 generator and synthetic fixtures |
| `d70385fa2d061b07e6929112aa3fecf0fd9d31b2` | test: add batch 03 intake and determinism coverage |
| *(this commit)* | docs: report batch 03 results and limitations |

## Test totals

- Baseline: **1,993 passed, 1 skipped, 0 failed**.
- Final: **2,056 passed, 1 skipped, 0 failed** (+63).
- Dedicated Batch 03 suites: `test_local_bar_intake.py` (40),
  `test_batch03.py` (13), `test_batch03_cli.py` (7),
  `test_batch03_documentation.py` (3) = **63**.
- The single skip is the pre-existing baseline skip (unchanged).

## Implemented contracts and CLIs

- Package `squeeze_core.acquisition.local_bar_intake`: `IntakeManifest`,
  `ColumnMappingProfile`, `RawArtifactDescriptor`, `ArtifactValidationReport`,
  `CanonicalMarketBar`, `NormalizedBarSet`, `RowDiagnostic`,
  `NormalizationDiagnostics`, `IntakeSummary`, `CaseAssociationMapping`,
  `CaseAssociationValidationResult`; the intake `contract`; the CSV adapter; the
  normalization engine; the case-association validator; JSONL/CSV serialization.
- `batch03.py` deterministic document builder + generator script.
- CLIs: `intake-validate-bundle`, `intake-inspect-artifact`,
  `intake-normalize-bars`, `intake-summary`,
  `intake-validate-case-association` (all offline).

## Generated fixture inventory

`tests/fixtures/acquisition/batch03/` (15 files): `intake-contract.json`,
`valid-raw-bars.csv`, `valid-intake-manifest.json`, `column-mapping-profile.json`,
`raw-artifact-manifest.json`, `artifact-validation.json`, `normalized-bars.jsonl`,
`normalized-bars.csv`, `normalization-diagnostics.json`, `intake-summary.json`,
`case-association-example.json`, `case-association-validation.json`,
`rejected-intake-examples.json`, `determinism-anchors.json`,
`batch-03-fixture-metadata.json`.

## Supported formats

CSV / delimited text (one complete reference adapter via an explicit mapping
profile). A canonical JSON adapter is deliberately out of scope for this batch.

## Validation and rejection behavior

Full reason-code taxonomy in `IntakeReasonCode`; policy in
`batch-03-validation-and-quarantine-policy.md`. `rejected-intake-examples.json`
demonstrates 17 rejection scenarios spanning artifact tamper, malformed/missing
values, invalid OHLC, coverage/ordering/duplicate/overlap violations, and the
current-for-historical / synthetic-for-historical / semantic barriers. Missing or
ambiguous evidence stays missing or ambiguous — bars are never repaired.

## Determinism verification

- `build_batch03_documents()` twice → byte-identical.
- Generator → `build/acquisition/batch-03/`: all 15 documents byte-identical to
  the committed fixtures.
- All five CLIs twice → byte-identical; normalize CLI output matches committed
  `normalized-bars.jsonl` / `.csv`.
- No CR/CRLF in any generated document; `.gitattributes` enforces LF.

## Compatibility verification

- Batch 01 fixture digest `a4a6ece91800e215baeb197a6f178505c526d49c672f3274365bde4f624b407a` — unchanged.
- Batch 02 fixture digest `eefed973fb1c7e709c52060c274bf57b6d641993ac96e9e08687e75e818e30c4` — unchanged.
- Archived parent repo `HEAD 0897562e05d75b812dd284de81dfafdfa1dea916`, clean.
- Archived submodule `HEAD 6dbefd1a6b271bfc48106c4aa002f211735551cd`, clean.
- Schema version remains `1.0.0`. No prior serialized bytes changed.

## Credential / network confirmation

No network access, no credentials, no provider account, no scraping, no archived
auth/TLS helper execution, no credential file access (`schwab_tokens.json`
untouched). The acquisition isolation guard statically proves the new package
imports no network/db/ML/dataframe library and makes no env/random/wall-clock
calls. No credential-like value appears in any committed fixture.

## Deviations from the preregistered plan

- The plan sketched separate `contract.py` / validation / case-association
  commits; they were grouped into one cohesive, independently-importable package
  commit (the package `__init__` imports every module, so a split would leave a
  non-importable intermediate commit). Behaviour and scope are unchanged.
- Two manifest fields beyond the plan's minimum list were added under the plan's
  explicit "at least" allowance — `data_time_basis` and (`value_authenticity`,
  `intended_use`) — to make the required current-for-historical and
  synthetic-for-historical rejections honest and testable. `session_coverage_policy`
  and optional `symbol_column` / `venue_column` were likewise added to support the
  continuity and symbol/venue-mismatch reason codes.

## Remaining limitations

- Only CSV is normalized; a JSON adapter is deferred.
- Only fixed-interval bars (minute/hour) are normalized; session-based daily bars
  are declared `UNSUPPORTED_INTERVAL` this batch.
- Named IANA timezones require the `tzdata` package, which is absent in this
  environment; fixtures therefore use UTC / numeric offsets. The
  ambiguous-local-time reason-code mapping is covered unconditionally, with an
  additional end-to-end assertion gated on IANA-DB availability (so the skip count
  is unchanged).
- No real market data is ingested; all bundles are synthetic infrastructure
  fixtures.

## Scope boundary

No outcome value entered any pre-outcome identity. No Phase 3A request/result, no
Phase 3B label or candidate, no scoring/ranking/prediction, and no modification of
Batch 01/02 evidence occurred. **Phase 3E was not started.**
