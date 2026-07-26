# Phase 3D Controlled Historical Acquisition Design

## Purpose and boundary

Phase 3D adds an offline, deterministic acquisition and curation layer for historical candidate cases. It expands the evidence pipeline without changing Phase 3A thresholds, Phase 3B policies or schemas, or Phase 3C analysis behavior. Curated cases are research inputs, not proof of predictive validity.

The enforced flow is:

1. preregister an acquisition plan;
2. record explicit discovery evidence;
3. inventory immutable raw artifacts and provider provenance;
4. normalize into separate derived artifacts;
5. review evidence availability and resolve historical security identity;
6. decide eligibility using outcome-blind policy;
7. freeze a detection boundary from discovery-time evidence;
8. serialize and hash the Phase 3A request and result;
9. capture retrospective outcome evidence in a separate manifest;
10. run the leakage audit and, only when it passes, adapt eligible bundles to unchanged Phase 3B contracts.

Outcome information is prohibited from discovery, identity resolution, evidence sufficiency, eligibility, boundary selection, and Phase 3A input construction. Missing historical evidence remains missing. A current provider observation cannot be represented as a historical value.

## Architecture

The additive `squeeze_core.acquisition` package owns Phase 3D contracts and behavior:

- `models.py` defines frozen Pydantic contracts, lifecycle states, classifications, and policy enums.
- `identifiers.py` creates UUIDv5 identities from canonical semantic content; wall-clock time and absolute paths never participate.
- `policies.py` loads exact versioned policy documents.
- `artifacts.py` validates explicit artifact manifests, byte length, SHA-256, media type, and duplicate content without altering source bytes.
- `identity_resolution.py`, `eligibility.py`, and `boundary_freeze.py` perform outcome-blind review steps.
- `leakage_guards.py` rejects prohibited outcome flow and blocks empirical publication after any failed audit.
- `curation.py` implements monotonic lifecycle transitions, append-only attempts, resumable batches, and immutable bundles.
- `publication.py` projects eligible bundles into existing Phase 3B registry and dataset candidate models without modifying Phase 3B contracts.
- `serialization.py`, `reports.py`, and `runner.py` provide canonical bytes, required interpretation language, and explicit-input orchestration.

All deterministic runtime remains standard-library plus the repository's pinned Pydantic dependency. It performs no network access, environment or credential reads, database access, GUI operations, provider authentication, or implicit filesystem scanning.

## Preregistered policies

Phase 3D freezes these independently versioned policies:

- `phase_3d_acquisition_plan_policy.v1`
- `phase_3d_candidate_discovery_policy.v1`
- `phase_3d_historical_inclusion_policy.v1`
- `phase_3d_historical_exclusion_policy.v1`
- `phase_3d_identity_resolution_policy.v1`
- `phase_3d_detection_boundary_policy.v1`
- `phase_3d_outcome_leakage_policy.v1`
- `phase_3d_unique_security_deduplication_policy.v1`

Only `PREREGISTERED` and `ACTIVE` plans may yield included cases. A criteria change creates a different deterministic identity. Outcome-access state is explicit and cannot be reset silently.

## Evidence and provenance

Every artifact is named by a stable relative path and verified using byte length and SHA-256. Provider provenance preserves event, observed, effective, published, received, and artifact timestamps independently, together with scope, historical/current state, revision state, and license reference. Restricted local artifacts remain local and are omitted from public projections.

Discovery, evaluation, and outcome manifests are separate contracts. Synthetic edge cases may test software but cannot become historical empirical cases. Manual discovery leads remain distinguishable from systematic source records, and original-platform surfaced status is never inferred from public evidence.

## Identity and deduplication

Resolution preserves every source claim and conflict across symbol, issuer, exchange, security type, provider identifiers, effective dates, corporate actions, symbol changes, mergers, delistings, and reuse risk. Symbol text alone is not a permanent identity when reuse is plausible.

The default empirical unit is a unique resolved security identity. The earliest eligible outcome-blind boundary is primary. Later boundaries may remain as explicitly dependent secondary observations; they never increase the independent-symbol count.

## Eligibility, boundary freeze, and leakage

Eligibility records every satisfied, missing, and failed condition. Missing short-pressure evidence may produce unknown or insufficient Phase 3A rules and does not by itself exclude a case. Later outcome, including a non-move, is not an eligibility input. Excluded attempts remain in the ledger with reason codes, evidence references, review notes, and remediation.

Boundary selection uses discovery evidence only. Permitted rules include first objective discovery time, first eligible completed bar at or after discovery, original-platform surfaced time, and reviewed manual reconstruction. Maximum later return, threshold crossing, or favorable classification can never select a boundary.

The leakage audit checks prohibited fields and manifest ordering, verifies that the plan, boundary, Phase 3A request, and Phase 3A result were frozen before outcome capture, and compares frozen hashes. Any failure blocks empirical publication while retaining the attempted case.

## Curation lifecycle and publication

Bundles advance monotonically through discovered, captured, normalized, identity-reviewed, eligibility-reviewed, boundary-frozen, evaluation-frozen, outcome-captured, research-evaluated, reviewed, and published states. Partial, blocked, excluded, rejected, and superseded records stay visible. Resume is identity-based and cannot create a duplicate attempt.

The Phase 3B adapter has two outputs: registry candidates for honestly incomplete attempts and dataset candidates only for complete, leakage-passing, non-synthetic bundles. BIYA's earliest boundary remains primary, its later boundary remains dependent, and existing artifact identifiers are preserved without reinterpretation. KLRS, LBGJ, SG, TRVI, SLS, and KLOS remain visible with their existing limitations or conflict state.

## Deterministic outputs

JSON uses canonical key ordering, stable tuple ordering, UTF-8, and LF. Markdown has fixed sections and wording. Absolute paths, retrieval wall-clock values, and unordered collection iteration do not influence identities or bytes. Every generator and CLI output is regenerated twice in verification.

## Explicit non-goals

Phase 3D performs no predictive validation, threshold changes, rule weighting, composite scoring, candidate ranking, recommendations, alerts, entry or exit logic, backtesting, profit-and-loss calculation, portfolio simulation, machine learning, permanent live provider integration, database persistence, authentication, paper trading, or live trading. Phase 3E is out of scope.
