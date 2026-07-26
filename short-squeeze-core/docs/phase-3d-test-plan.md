# Phase 3D Test Plan

## Strategy

Phase 3D is developed test-first. Each behavior begins with a focused failing test, is implemented minimally, and is followed by the relevant Phase 3D suite and compatibility checks. Tests are offline and use explicit local fixtures or unrelated synthetic values.

## Contract and policy tests

- frozen Pydantic models reject mutation and extra fields;
- schema version stays `1.0.0` and exact policy versions are required;
- UUIDv5 identities are stable, order-canonical, independent of absolute paths and informational timestamps, and change when semantic criteria change;
- plan states cover draft, preregistered, active, closed, and superseded, with inclusion restricted to preregistered or active plans;
- discovery, inclusion, exclusion, identity, boundary, leakage, and deduplication documents load byte-deterministically.

## Artifact and provenance tests

- explicit manifests validate SHA-256, byte length, media type, relative paths, missing files, duplicates, and restricted-local classification;
- normalization never modifies a source artifact and derived records use separate paths and classifications;
- event, observed, effective, published, received, and artifact times remain distinct;
- provider scope and revision status remain explicit;
- current values cannot masquerade as historical evidence.

## Identity, eligibility, and boundary tests

- resolved, partial, conflicted, and unresolved identities preserve all claims;
- symbol reuse, reverse splits, mergers, delistings, and symbol changes are represented without overwriting conflict;
- every inclusion condition and exclusion reason is exercised;
- missing short-pressure evidence and a later non-move do not automatically exclude a case;
- outcome fields are inaccessible to eligibility logic and fabricated evidence is rejected;
- boundaries cover objective discovery, completed-bar, original-platform, and reviewed manual reconstruction paths;
- ties are deterministic, missing or ambiguous boundaries remain blocked, and outcome-aware or maximum-return selection fails.

## Leakage and lifecycle tests

- each prohibited outcome flow path emits its exact diagnostic;
- outcome capture before plan, boundary, request, and result freeze fails;
- discovery/evaluation and outcome manifests must be separate;
- a plan changed after outcome access fails the audit;
- failed audits block empirical publication without deleting attempts;
- lifecycle transitions are monotonic, invalid jumps fail, resume is stable, and duplicate attempts are not created;
- included, partial, blocked, excluded, rejected, and complete bundles remain serializable.

## Migration and publication tests

- BIYA earliest and latest boundaries preserve prior IDs, share one identity, and mark earliest primary and latest dependent;
- KLRS, LBGJ, SG, TRVI, SLS, and KLOS migrate without reinterpretation;
- valid registry and dataset candidates validate against unchanged Phase 3B models;
- incomplete cases are registry-only, synthetic cases remain non-empirical, dependent secondary boundaries are explicit, and leakage failure blocks publication;
- Phase 3B serializers remain byte-identical for existing fixtures.

## CLI, fixtures, reports, and isolation

- `validate-acquisition-plan`, `curate-historical-cases`, `audit-outcome-leakage`, and `render-acquisition-report` require explicit local inputs, return structured failures, do not scan implicitly, and produce repeated byte-identical output;
- fixtures cover the 45 required edge cases and carry sanitized classifications;
- the anchor manifest includes every required policy, migration, bundle, candidate, report, CLI, and collection hash;
- reports contain all required interpretation statements and disclose classifications, missingness, exclusions, dependency, and leakage status;
- AST-aware isolation tests reject network clients, provider SDKs, environment or credential reads, database and GUI imports, random or clock-based identity, scientific or ML stacks, trading APIs, scoring, ranking, recommendations, alerts, optimization, backtesting, and profit-and-loss logic.

## Compatibility and verification commands

Run focused Phase 3D tests during development, then:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\acquisition --basetemp=.pytest-run-phase3d-acquisition
.\.venv\Scripts\python.exe -m pytest tests\analysis --basetemp=.pytest-run-phase3d-analysis
.\.venv\Scripts\python.exe -m pytest tests\research --basetemp=.pytest-run-phase3d-research
.\.venv\Scripts\python.exe -m pytest tests\evaluation --basetemp=.pytest-run-phase3d-evaluation
.\.venv\Scripts\python.exe -m pytest tests\validation --basetemp=.pytest-run-phase3d-validation
.\.venv\Scripts\python.exe -m pytest tests\readiness --basetemp=.pytest-run-phase3d-readiness
.\.venv\Scripts\python.exe -m pytest tests\metrics --basetemp=.pytest-run-phase3d-metrics
.\.venv\Scripts\python.exe -m pytest tests\compatibility --basetemp=.pytest-run-phase3d-compat
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-run-phase3d-final
```

Before approval, regenerate every Phase 3D fixture, report, collection, and CLI output at least twice and compare bytes; compare all Phase 1–3C manifests and committed fixtures with `14d35abfc9aacc6f2f4adaa3ad264950ec556d17`; verify tags, remotes, merge base, archived commits, branch, and working tree.
