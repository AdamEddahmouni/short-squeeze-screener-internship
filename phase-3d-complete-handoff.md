# Short-Squeeze Project — Complete Phase 3D Handoff

This document is the authoritative fresh-session handoff after completion of Phase 3D.

Treat this file and the repository contents as the complete project state. Verify repository claims before making changes. Do not rely on prior chat context.

## 1. Current decision

**Phase 3D approved.**

Phase 3D built and verified controlled historical-case acquisition infrastructure. It did not perform a new external historical-source collection batch and did not begin Phase 3E.

The only recommended next task is:

> Run a separately approved, preregistered historical-source collection batch that adds independent real-symbol artifacts to the Phase 3D intake, then curate and publish only cases that pass identity, provenance, eligibility, boundary-freeze, and leakage audits.

Do not begin that collection batch, Phase 3E, threshold optimization, predictive modeling, scoring, ranking, recommendations, alerts, backtesting, paper trading, or live trading without separate user approval.

## 2. Workspace and repositories

Workspace root:

```text
C:\Users\adame\Desktop\short-squeeze-project
```

Implementation repository:

```text
C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core
```

All implementation work must remain in `short-squeeze-core`. Archived repositories are forensic evidence and remain read-only.

### Final implementation state

```text
Branch:       phase/3d-historical-case-acquisition
Starting HEAD: 14d35abfc9aacc6f2f4adaa3ad264950ec556d17
Final HEAD:    67459c351903a4e34a86f9849b157cb7fde2c395
Merge base:    14d35abfc9aacc6f2f4adaa3ad264950ec556d17
Remotes:       none
Push status:   nothing pushed
Merge status:  nothing merged
Schema:        1.0.0
```

The tracked working tree is clean. One unrelated file was already untracked before Phase 3D began and was deliberately preserved untouched:

```text
docs/phase-3c-complete-handoff.md
```

Do not delete, edit, or commit that file without explicit user direction.

### Tag

```text
phase-1-rc1 -> f903d4d144d3f7e9717b1ab8e684da406d7968fb
```

### Archived repository checkpoints

Verify read-only:

```text
0897562e05d75b812dd284de81dfafdfa1dea916
6dbefd1a6b271bfc48106c4aa002f211735551cd
84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8
```

Do not reset, checkout, clean, commit, merge, rebase, format, or rewrite archived repositories.

## 3. Standing credential rule

The project and forensic repositories are local-only.

Do not redact, mask, remove, replace, rotate, alter, or rewrite credentials, tokens, authentication parameters, API keys, cookies, or fragments in local source files, logs, documentation, inventories, fixtures, or forensic artifacts unless the user explicitly authorizes that exact change.

Preserve local artifacts byte-for-byte. Do not print credentials in tests, reports, command output, or completion messages. Use unrelated dummy values in synthetic tests.

## 4. Phase history

### Phase 1

Canonical point-in-time evidence models, provider-neutral observations, deterministic identities, canonical serialization, replay, and offline evidence adapters.

### Phase 2A–2D

Deterministic market metrics, normalized activity metrics, short-pressure metrics, and evidence-readiness diagnostics.

### Phase 2V

BIYA forensic validation with final conclusion:

```text
OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED
```

### Phase 3A

Transparent independent rule evaluation across:

- momentum discovery;
- short-pressure confirmation;
- catalyst evidence;
- evidence validity.

No score, rank, recommendation, alert, or Prime/Subprime label exists.

### Phase 3B

Deterministic multi-candidate research evaluation with explicit case registry, provisional detection policy, retrospective outcome policy, immutable classification truth table, historical and synthetic cases, and JSON/JSONL/CSV datasets.

### Phase 3C

Deterministic descriptive analysis with explicit cohorts, outcome-blind earliest-boundary selection, exact proportions, Wilson intervals, confusion matrices, prevalence, missingness, dependence analysis, fixed reports, fixtures, and anchors.

The completed historical empirical cohort still contains only one independent symbol: BIYA.

### Phase 3D

Controlled, offline, deterministic acquisition and curation infrastructure with:

- preregistered acquisition plans;
- explicit discovery sources;
- raw artifact inventories and SHA-256 validation;
- separate provider time dimensions;
- historical/current provenance guards;
- identity resolution and conflict preservation;
- deterministic evidence-sufficiency review;
- preregistered eligibility and exclusions;
- outcome-blind boundary freezing;
- outcome leakage audits;
- monotonic bundle lifecycle;
- append-only, resumable case ledger;
- BIYA and incomplete-case migration;
- unchanged Phase 3B publication adapters;
- four offline CLI commands;
- deterministic fixtures, reports, and anchors;
- additive compatibility and AST isolation guards.

## 5. Phase 3D data-flow boundary

The required sequence is:

```text
PREREGISTERED ACQUISITION PLAN
→ SOURCE DISCOVERY
→ RAW ARTIFACT CAPTURE
→ POINT-IN-TIME NORMALIZATION
→ EVIDENCE-AVAILABILITY REVIEW
→ IDENTITY RESOLUTION
→ ELIGIBILITY DECISION
→ DETECTION-BOUNDARY FREEZE
→ PHASE 3A EVALUATION INPUT
→ FROZEN PHASE 3A RESULT
→ SEPARATE OUTCOME CAPTURE
→ PHASE 3B RESEARCH RESULT
→ PHASE 3C ANALYSIS INPUT
```

Outcome information is prohibited from:

- source selection for a frozen cohort;
- identity resolution;
- eligibility decisions;
- detection-boundary selection;
- Phase 3A input construction;
- missingness resolution;
- historical-provider substitution decisions.

Outcome capture occurs only after the acquisition plan, boundary, Phase 3A request, and Phase 3A result are frozen.

## 6. Architecture

The additive runtime package is:

```text
src/squeeze_core/acquisition/
├── __init__.py
├── artifacts.py
├── boundary_freeze.py
├── curation.py
├── eligibility.py
├── fixture_generation.py
├── identifiers.py
├── identity_resolution.py
├── leakage_guards.py
├── migration.py
├── models.py
├── plans.py
├── policies.py
├── policy_documents/
├── provenance.py
├── publication.py
├── reports.py
├── runner.py
├── serialization.py
└── sufficiency.py
```

### Architectural rules

- Phase 3D is additive. Phase 1–3C contracts and schemas were not extended.
- Deterministic runtime uses only the standard library, Pydantic, and existing local contracts.
- Runtime performs no network access, provider authentication, credential reads, environment reads, database access, GUI behavior, or implicit directory scanning.
- Inputs are explicit local paths.
- UUIDv5 identities exclude wall-clock time and absolute paths.
- JSON is canonical UTF-8 with stable ordering.
- Reports have fixed wording and LF line endings.
- Synthetic fixtures never become empirical historical cases.
- Restricted local artifacts never enter public exports.

## 7. Versioned policies

The exact policies are:

```text
phase_3d_acquisition_plan_policy.v1
phase_3d_candidate_discovery_policy.v1
phase_3d_historical_inclusion_policy.v1
phase_3d_historical_exclusion_policy.v1
phase_3d_identity_resolution_policy.v1
phase_3d_detection_boundary_policy.v1
phase_3d_outcome_leakage_policy.v1
phase_3d_unique_security_deduplication_policy.v1
```

Only `PREREGISTERED` and `ACTIVE` plans may yield included cases. `DRAFT`, `CLOSED`, and `SUPERSEDED` plans remain reviewable but cannot produce included cases.

Changing semantic plan criteria changes plan identity. Informational creation time does not affect identity.

## 8. Initial pilot plan

```text
Plan ID: phase-3d-controlled-pilot
Deterministic ID: bde5148e-f3d4-551b-b176-269e6b2d4e48
Status: PREREGISTERED
Date range: 2024-01-01 through 2024-12-31
Maximum cases: 20
Minimum cases: 0
Population: US-listed common stocks in the explicit pilot source manifest
Sampling: source order, then unique-security-identity deduplication
Discovery source: explicit public historical market-event feed
Outcome blinding: OUTCOME_BLINDED
```

The pilot deliberately claims no new complete historical case. A small, partial, blocked, or empty complete cohort is not a Phase 3D failure.

## 9. Artifact and provider provenance

Every artifact record preserves:

- stable relative path;
- file name and media type;
- byte length and SHA-256;
- source class;
- provider provenance ID;
- fixture classification;
- capture method;
- observed, effective, and published times;
- content and sensitive-content status.

Provider provenance separately preserves:

- event time;
- observed time;
- effective time;
- publication time;
- receipt time;
- artifact time;
- provider scope;
- access method;
- historical/current state;
- revision status;
- terms or license reference.

Current data cannot masquerade as historical data. Unknown provider scope is explicit and blocks unsupported historical claims.

### Pilot artifact inventory

```text
Declared artifacts: 1
Providers: 1
Source class: PUBLIC_MARKET_EVENT_FEED
Fixture class: SANITIZED_HISTORICAL_FIXTURE
Restricted local artifacts: 0
Duplicate artifacts: 0 in the pilot
Unsupported artifacts: 0 in the pilot
```

The public fixture does not embed the raw pilot payload. The pilot case therefore remains `DISCOVERED`, pending evidence availability and artifact review.

## 10. Identity and sufficiency

Identity states are:

```text
RESOLVED
PARTIALLY_RESOLVED
CONFLICTED
UNRESOLVED
```

Claims preserve symbol, issuer, exchange, security type, provider identifiers, effective dates, corporate actions, reverse splits, mergers, delistings, symbol changes, and symbol-reuse risk.

Symbol text alone is not a permanent identity when historical reuse is plausible. Conflicting source claims remain present and are never overwritten.

Evidence-sufficiency states are:

```text
SUFFICIENT_FOR_PHASE_3A
SUFFICIENT_FOR_PHASE_3B_OUTCOME_ONLY
SUFFICIENT_FOR_REGISTRY_ONLY
PARTIAL
BLOCKED
CONFLICTED
UNUSABLE
```

Missing short-pressure evidence does not automatically prevent Phase 3A sufficiency. It remains missing, unknown, or insufficient.

## 11. Eligibility and exclusions

Inclusion requires:

- preregistered or active plan;
- in-range, in-population discovery;
- discovery provenance;
- validated required artifacts;
- resolvable identity;
- deterministic detection boundary;
- objective market evidence;
- a Phase 3A request constructible without fabrication;
- no outcome-aware selection evidence.

Later performance, including a non-move, is never an eligibility input.

The exact exclusion vocabulary includes:

```text
OUTSIDE_PREREGISTERED_DATE_RANGE
OUTSIDE_PREREGISTERED_POPULATION
DUPLICATE_SYMBOL
DUPLICATE_DISCOVERY
IDENTITY_UNRESOLVED
IDENTITY_CONFLICT
DETECTION_BOUNDARY_UNRESOLVED
MARKET_DATA_UNAVAILABLE
NO_COMPLETED_BAR_AT_BOUNDARY
DISCOVERY_PROVENANCE_MISSING
SOURCE_ARTIFACT_MISSING
SOURCE_ARTIFACT_HASH_MISMATCH
OUTCOME_LEAKAGE_DETECTED
OUTCOME_AWARE_SELECTION_SUSPECTED
POST_EVENT_SOURCE_ONLY
MODERN_DATA_MISREPRESENTED_AS_HISTORICAL
PROVIDER_SCOPE_UNRESOLVED
CORPORATE_ACTION_UNRESOLVED
SYMBOL_REUSE_UNRESOLVED
ACQUISITION_PLAN_NOT_PREREGISTERED
CASE_REQUIRES_FABRICATED_EVIDENCE
MANUAL_REVIEW_REQUIRED
```

Excluded attempts remain in the append-only ledger.

## 12. Detection-boundary freeze

Permitted rules are:

```text
FIRST_OBJECTIVE_DISCOVERY_TIMESTAMP
FIRST_ELIGIBLE_COMPLETED_BAR_AT_OR_AFTER_DISCOVERY
ORIGINAL_PLATFORM_SURFACED_TIMESTAMP
MANUALLY_RECONSTRUCTED_WITH_EVIDENCE
```

Tie-breaking is deterministic by timestamp and source-artifact ID.

The following are prohibited:

- maximum later return;
- earliest point before a known spike;
- best-performing interval;
- most favorable classification;
- outcome threshold crossing;
- later news timing selected with hindsight.

An outcome-aware boundary rule is explicitly rejected in fixtures and tests.

## 13. Outcome leakage

Required diagnostics include:

```text
OUTCOME_DATA_PRESENT_IN_DISCOVERY_INPUT
OUTCOME_DATA_PRESENT_IN_ELIGIBILITY_INPUT
OUTCOME_DATA_PRESENT_IN_BOUNDARY_INPUT
OUTCOME_DATA_PRESENT_IN_EVALUATION_INPUT
OUTCOME_ARTIFACT_CAPTURED_BEFORE_EVALUATION_FREEZE
OUTCOME_AWARE_SELECTION_INDICATOR
MAXIMUM_RETURN_SELECTION_INDICATOR
POST_EVENT_ARTICLE_USED_AS_DISCOVERY_SOURCE
ACQUISITION_PLAN_CHANGED_AFTER_OUTCOME_ACCESS
LEAKAGE_AUDIT_PASSED
LEAKAGE_AUDIT_FAILED
```

Failed audits block empirical publication, return a nonzero CLI status, and retain the attempted case.

Fixture audit results:

```text
Passing audits: 1
Failing audits: 1
Blocked publications: 1
Failure: OUTCOME_DATA_PRESENT_IN_DISCOVERY_INPUT
```

The actual pilot contains no retrospective outcome and makes no empirical publication claim.

## 14. Curation lifecycle

The monotonic lifecycle is:

```text
DISCOVERED
→ ARTIFACTS_CAPTURED
→ NORMALIZED
→ IDENTITY_REVIEWED
→ ELIGIBILITY_REVIEWED
→ BOUNDARY_FROZEN
→ EVALUATION_FROZEN
→ OUTCOME_CAPTURED
→ RESEARCH_EVALUATED
→ REVIEWED
→ PUBLISHED
```

Honest terminal review states include:

```text
PARTIAL
BLOCKED
EXCLUDED
REJECTED
SUPERSEDED
```

Invalid lifecycle jumps fail. Reprocessing an identical attempt is idempotent. Reusing an attempt ID for different semantic content fails.

## 15. Pilot ledger

```text
Attempted: 1
Discovered: 1
Included: 0
Excluded: 0
Partial: 0
Blocked: 0
Complete: 0
Unique identities: 1
Repeated boundaries: 0
```

Interpretation: no new complete historical case is claimed by the pilot.

## 16. BIYA migration

`BIYA_EARLIEST_BOUNDARY` remains the primary boundary.

`BIYA_LATEST_BOUNDARY` remains a dependent secondary boundary and points to the earliest bundle.

Both preserve prior:

- case IDs;
- source artifact IDs;
- classifications;
- limitations;
- Phase 3B registry entries;
- Phase 3B dataset rows.

BIYA represents one independent security identity, not two independent observations. Nothing in the migration reinterprets prior artifacts or claims that BIYA was collected under the new preregistered pilot plan.

## 17. Incomplete-case migration

```text
KLRS: partial; no defensible complete detection snapshot survives
LBGJ: partial; no defensible complete detection snapshot survives
SG:   partial; original-platform status remains unknown
TRVI: partial; original-platform status remains unknown
SLS:  partial; original-platform status remains unknown
KLOS: blocked by conflicting identity
```

All remain registry-visible.

## 18. Phase 3B publication adapter

The adapter returns existing typed Phase 3B objects unchanged after validating bundle/case identity and publication eligibility.

```text
Registry-ready migrations: 8
Dataset-ready migrations: 2 BIYA boundaries
Registry-only migrations: 6
Blocked migrations: 1
Dependent secondary boundaries: 1
Synthetic empirical candidates: 0
```

Dataset publication requires a complete, reviewed, leakage-passing, non-synthetic bundle. Incomplete attempts may be registry-only. Phase 3B schemas and serializers remain unchanged.

## 19. Offline CLI

The commands are:

```text
validate-acquisition-plan
curate-historical-cases
audit-outcome-leakage
render-acquisition-report
```

Examples:

```powershell
cd C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core

.\.venv\Scripts\python.exe -m squeeze_core validate-acquisition-plan `
  --plan tests\fixtures\acquisition\phase_3d_acquisition_plan.json

.\.venv\Scripts\python.exe -m squeeze_core curate-historical-cases `
  --plan tests\fixtures\acquisition\phase_3d_acquisition_plan.json `
  --source-manifest tests\fixtures\acquisition\phase_3d_source_manifest.json `
  --artifact-manifest tests\fixtures\acquisition\phase_3d_artifact_manifest.json `
  --output build\acquisition\phase_3d_batch.json

.\.venv\Scripts\python.exe -m squeeze_core audit-outcome-leakage `
  --batch build\acquisition\phase_3d_batch.json `
  --output build\acquisition\phase_3d_leakage_audit.json

.\.venv\Scripts\python.exe -m squeeze_core render-acquisition-report `
  --batch build\acquisition\phase_3d_batch.json `
  --format markdown `
  --output build\acquisition\phase_3d_curation_report.md
```

All commands require explicit local inputs. They perform no implicit filesystem scan and no network access. Invalid input produces structured JSON and a nonzero exit code.

## 20. Fixtures and outputs

The 20 required fixtures are in:

```text
tests/fixtures/acquisition
```

```text
expected_phase_3d_acquisition_metadata.json
phase_3d_acquisition_plan.json
phase_3d_artifact_manifest.json
phase_3d_batch_summary.json
phase_3d_biya_migrated_bundles.json
phase_3d_boundary_policy.json
phase_3d_case_attempt_ledger.json
phase_3d_curation_report.md
phase_3d_deduplication_policy.json
phase_3d_discovery_policy.json
phase_3d_exclusion_policy.json
phase_3d_fixture_metadata.json
phase_3d_identity_resolution_policy.json
phase_3d_inclusion_policy.json
phase_3d_incomplete_case_migrations.json
phase_3d_leakage_audit.json
phase_3d_leakage_policy.json
phase_3d_phase3b_dataset_candidates.json
phase_3d_phase3b_registry_candidates.json
phase_3d_source_manifest.json
```

Per-file SHA-256 values are in `phase_3d_fixture_metadata.json`.

Fixture-metadata SHA-256:

```text
a5dd3695b792a217f2d13f32cc18b426c6d36c81112899e3f419d1c57a692154
```

Repeated command outputs were byte-identical:

```text
Curated batch:     030d17cd9ea6151910ad63afd38ba289472b43b4a99180b847fb695339c6d1ad
Leakage collection: 0e8372993ed6b621137c4f678ba44ab10cb3a346735405e3a844b644208dc279
Markdown report:   cd2c526c49f86862d1940dfeac18543178788eae7011ffa55fc09e3e6eb0bbf7
```

No credentials, sensitive raw artifacts, or restricted local artifacts are included in public fixtures.

## 21. Phase 3D anchor hashes

All anchor values are true SHA-256 digests:

```text
acquisition_plan f7b39c7fa33854eb7e34fd5fde6d19f44001eefe6339448324ddfef61f79fc92
artifact_manifest a897d459081312b2fd624e88a0144d9c044add402b44f71323641b577f28b24e
batch_summary 5c2de3c45aa09697ad886e06f60130916e886b13e2320d257ae8c6f886f4ba44
biya_duplicate_group f362f5797755b37ec1632fb01a8d1f875a8c3a1482eb27fb49c913b760e677b9
biya_earliest_migration eb853d96bbad8e91b44ceaca71f636bba7925cebe5caf6e7b38f514b4c5e65c8
biya_latest_migration 011680fd81fe1a1511edd803c903e71184d121d6a1cdcf2176e0510435a64257
blocked_curated_bundle 0aff2b3fda883b2f3ce1eeab92eea054da1cdc2e92b2996a53cc5e82de35b99f
boundary_policy f313d36d30d3c24fa4c00c65d4a0a080e3d6f4491d0b0b89cb482d52d2fbd59c
case_attempt_ledger 492ef6216dea9457bcfa0c0b17be8cec4daf9c8e523140bfc898ba65328888c1
complete_curated_bundle 911fcf5b9370dd2d2cdeed4edf2451f62ddcf6fe1d60a4110f18566e7f5bdb21
conflicted_identity_resolution 1bb6b45fa8ebf9d5c6b0019b82060bebbe34b6a3fd5aa77fd60d2d74e5f7fa70
curation_report 219b2f745371639dc15d474d0f4a84f6debbaf04b6c05fd374aeae2b7cec5e50
deduplication_policy 28eeccd35c489fd560a97aefc999ff70f756c27aa4bbdb983d7543c6695aa6cc
discovery_policy eb90062b304d0f92781139e557b4b49c6348e9c8a51b847eb5787eab61f675c4
excluded_eligibility_decision 5e762384def23dfa3c959c762641f8685885438a36f508f913fd6b1bf597dd0f
exclusion_policy 986824100641d78e20c81b49f5e17b8677cdb5c2c8bf4458594b1cca41ac9751
failed_leakage_audit 842064d37430027a0c814fde6dab626c304faf924a22197f5c50ae0d1da1c9cf
identity_resolution_policy f10ca0d0fe50c1e9c234513c322013a7e6fdf8d22647a41001234c9634af4c71
inclusion_policy 68b2b1e89aca8218afdbe6f53590fc9527ad31e2d0f3995e2e3014a06f2243a3
klos_conflict_migration f8086f934805a1ebebd355396cc733658ec3a38a9393cda5a41ddcbf686f1047
klrs_migration 06c52241c508d0d863cefdd265a8de4f60c25451ef032fcab717f3581963a31e
lbgj_migration e1ac7ff0eb2eaf8d52082cf3d231c953ae7c02dc3484d4004961deb6c0ef0fc1
leakage_policy edd5b1b50eb148ef3c50013b71a73694f1ea799df3b1edd4c0551f1bf00a3ed1
outcome_aware_boundary_rejection b9cc8c62f79f43366083b9a745a926c8610de8c50ad6c9444d32ff66de607763
partial_curated_bundle 8d16e283020a1fc7bab9c434f066f961b41dbafde07670224b99777bebc686eb
phase_3d_cli_output 3306d3f336ff85630b320da48ffa43a0c8dba5c80b21f405121a9277f7014eb3
phase_3d_leakage_cli_output 6043a023b1ab7ab7c2806cf43537fba60512005c55c9162c3aea85855e508781
phase3b_dataset_candidate 4d5d1d215abb3bb1a9501bd71215acc616e2fc73549fea0345e5a8216d962e73
phase3b_registry_candidate ef15e8c882b9bccd8869c376b0d39a723cb1d894d7148f1da85ead2f4af7d892
registry_only_candidate 9f28e408e12195623851c51667ea1b5c20f855da895ee7c85438a83f0e51a61a
rejected_curated_bundle e7db9651df659a481c20eb4fed6c359b190301969abc6d2771678c5e777fb902
serialized_phase_3d_collection 70774639dc2c348f82ee1e37cfa122a9583dfeafb158275b0ac40dd0580e7637
sg_migration 7ef08cbb9a5d2c003912d60d915aa0b711cb2a9f2126ec5ce5ecdd0226552399
sls_migration fd37c7a7902a3894fcfe4cdb053477d3cae6f441a2bb0417f2ec9379ce54f387
source_manifest 0348a25a7f8d341aa120cac9395cf56a492e2824b0997568032ae037e624c290
trvi_migration 6ab5898ac2d8d2535b4a0a0061868b7ec6e870705447476de68c88e67e31495a
valid_boundary_freeze e96f6d26da3b83d3aba8494bc0e1d9ebe5b18b82f388cdeee2c2e20ba936f738
valid_eligibility_decision d061c9083a821834953d34c24a952ef67e13d270fa4520df4521b943732be170
valid_identity_resolution 4b038c340a6bf21e5475da018722631db1e7b78a10439917a655e3ff8027339d
valid_leakage_audit c1431d1898f1be8e60cf45f08450af0d8101d22b7a8d798330896dc526df5e52
```

## 22. Verification evidence

Baseline before Phase 3D:

```text
1,893 passed
1 skipped
0 failed
```

Final focused totals:

```text
Acquisition:   52 passed
Analysis:     120 passed
Research:      65 passed
Evaluation:    50 passed
Validation:   367 passed
Readiness:    124 passed
Metrics:      453 passed
Compatibility:133 passed
```

Final full suite at HEAD `67459c351903a4e34a86f9849b157cb7fde2c395`:

```text
1,948 passed
1 skipped
0 failed
```

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  --basetemp=.pytest-run-phase3d-final-4
```

The 20 fixtures and all 40 anchors regenerated byte-identically. All four Phase 3D commands were run repeatedly and their output bytes compared.

## 23. Phase 3D commits

```text
67459c3 fix: store phase 3d anchors as sha256
45e9af7 docs: record final phase 3d verification totals
a98134f fix: align phase 3d pilot summary state
0fac05e chore: finalize phase 3d controlled acquisition
1c9e7d6 test: integrate phase 3d compatibility guards
7f63a67 feat: harden historical provenance and sufficiency review
85637c8 docs: document phase 3d controlled acquisition
fe6de63 test: add phase 3d fixtures and anchors
79fe994 feat: add offline phase 3d acquisition outputs
4bf765d feat: add phase 3b acquisition publication adapter
239755c feat: add deterministic acquisition qualification
beb221f feat: add phase 3d acquisition contracts and policies
d46cfb6 docs: specify phase 3d controlled historical acquisition
```

Do not amend, squash, rebase, merge, or push these commits unless the user explicitly authorizes it.

## 24. Documentation map

Primary Phase 3D documentation:

```text
docs/phase-3d-design.md
docs/phase-3d-test-plan.md
docs/phase-3d-acquisition-plan-policy.md
docs/phase-3d-source-and-provider-provenance.md
docs/phase-3d-artifact-intake.md
docs/phase-3d-identity-resolution.md
docs/phase-3d-inclusion-and-exclusion-policy.md
docs/phase-3d-detection-boundary-freeze.md
docs/phase-3d-outcome-leakage-prevention.md
docs/phase-3d-case-curation-workflow.md
docs/phase-3d-phase3b-publication-adapter.md
docs/phase-3d-biya-migration.md
docs/phase-3d-progress.md
docs/superpowers/plans/2026-07-22-phase-3d-historical-case-acquisition.md
```

ADRs:

```text
docs/adr/0059-acquisition-plans-are-preregistered-before-outcome-review.md
docs/adr/0060-outcome-artifacts-remain-separate.md
docs/adr/0061-missing-historical-evidence-is-never-fabricated.md
docs/adr/0062-current-values-cannot-substitute-for-historical-values.md
docs/adr/0063-excluded-attempts-remain-in-the-ledger.md
docs/adr/0064-unique-security-identity-is-the-empirical-unit.md
docs/adr/0065-phase-3d-does-not-optimize-prior-policies.md
```

## 25. Compatibility

- Phase 1–3C manifests and fixtures remain byte-unchanged.
- Schema remains `1.0.0`.
- Phase 3D is additive under `squeeze_core.acquisition`.
- Only the shared CLI entry point and additive compatibility allowlists changed outside the new package.
- Existing Phase 3B objects serialize unchanged through the publication adapter.
- Existing BIYA cases migrated without reinterpretation.
- Synthetic cases remain non-empirical.
- Prior CLI behavior remains unchanged.

## 26. Required interpretation language

Every Phase 3D curation report must continue to state:

- Phase 3D builds controlled historical acquisition infrastructure.
- Curated cases are not proof of predictive validity.
- Inclusion is based on preregistered criteria, not later outcome.
- Detection boundaries are frozen before retrospective outcome capture.
- Missing historical evidence is retained as missing.
- Current provider data is not silently treated as historical evidence.
- Excluded and blocked attempts remain visible.
- Repeated boundaries for one symbol are dependent observations.
- Synthetic fixtures test software behavior only.
- No Phase 3A threshold was changed.
- No Phase 3B policy was optimized.
- No scoring, ranking, recommendation, alert, backtest, P&L, or trading simulation was performed.

## 27. Remaining limitations

Phase 3D does not include:

- predictive validation;
- threshold optimization;
- rule weighting;
- composite scoring;
- candidate ranking;
- recommendations;
- alerts;
- entry or exit logic;
- P&L;
- backtesting;
- portfolio simulation;
- machine learning;
- permanent live-provider integrations;
- database persistence;
- authentication;
- paper trading;
- live trading.

There are still no newly completed independent real-symbol cases beyond the existing BIYA evidence. This is not a Phase 3D infrastructure failure. A separately approved collection batch is required to expand the empirical cohort.

## 28. Fresh-session verification checklist

Before any new work:

```powershell
cd C:\Users\adame\Desktop\short-squeeze-project\short-squeeze-core

git status
git status --short
git branch --show-current
git rev-parse HEAD
git merge-base HEAD 14d35abfc9aacc6f2f4adaa3ad264950ec556d17
git remote -v
git tag --list
git rev-list -n 1 phase-1-rc1
```

Expected:

```text
Branch: phase/3d-historical-case-acquisition
HEAD: 67459c351903a4e34a86f9849b157cb7fde2c395
Merge base: 14d35abfc9aacc6f2f4adaa3ad264950ec556d17
Remotes: none
Only pre-existing untracked file: docs/phase-3c-complete-handoff.md
```

Run the final suite with a fresh explicit temporary path:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  --basetemp=.pytest-run-post-phase3d-handoff
```

Expected current total:

```text
1,948 passed
1 skipped
0 failed
```

Do not use the locked `.pytest-tmp` path. Do not broadly delete old pytest directories.

## 29. Stop conditions for future work

Stop and report before continuing if:

- repository state could cause work loss or misattribute existing work;
- an archived repository would require modification;
- a prior anchor changes unexpectedly;
- Phase 3B or Phase 3C needs a breaking schema change;
- outcome information would be needed for discovery, eligibility, identity, or boundary selection;
- historical evidence would need to be fabricated;
- current values would need to masquerade as historical values;
- artifact provenance cannot be preserved;
- deterministic regeneration fails;
- scoring, ranking, optimization, recommendations, alerts, backtesting, P&L, or trading logic becomes necessary.

Incomplete, excluded, and blocked cases are expected. A small batch or no new complete case is not itself a blocker.

## 30. Next authorized task boundary

No next task has been authorized by this handoff alone.

When separately approved, the next task should be exactly one preregistered historical-source collection batch using explicit local artifacts. It should:

1. freeze the plan before outcome review;
2. capture source-defined positive, negative, non-moving, and unevaluable attempts;
3. preserve raw bytes, hashes, and provider provenance;
4. keep discovery, evaluation, and outcome artifacts separate;
5. resolve unique historical security identities;
6. freeze boundaries using discovery-time evidence only;
7. serialize and hash Phase 3A requests and results before outcome capture;
8. audit leakage;
9. publish only eligible, leakage-passing cases through unchanged Phase 3B adapters;
10. retain every excluded, partial, blocked, and duplicate attempt.

Do not begin Phase 3E automatically.
