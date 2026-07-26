# Batch 14 Independent Prime Dashboard Design

**Status:** Approved on 2026-07-25

**Starting checkpoint:** `5ac17f2d81d17a32b959c252a4dea4fc0a8c829d`

**Working branch:** `batch/independent-prime-dashboard-railway-14`

## Purpose

Batch 14 adds three separately evaluated research methodologies, a comparison dashboard,
provider-aware deployment modes, a stable read-only API, and Railway deployment support.
It preserves the canonical 25-rule Phase 3A evaluator and every frozen research artifact.
The peer email is reference material only; no peer code, architecture, missing formula, or
output is copied.

The application must display this label prominently:

> EXPERIMENTAL RESEARCH CLASSIFICATION — NOT PREDICTIVE VALIDATION

No output is a probability, expected return, trading recommendation, buy/sell signal, or
claim of validated performance.

## Branch and prior-work integration

The branch is created from the required Batch 13 checkpoint. Eleven already committed,
independently reviewed Finviz/provider commits from
`batch/authorized-finviz-activation-14` are cherry-picked in their original order. This
retains legitimate provider work without making the later branch the starting checkpoint.
The protected untracked `docs/phase-3c-complete-handoff.md` is never added or changed.

## Architecture

Methodology calculations live in a new backend-only package under
`apps/research_screener/methodologies/`. Policy definitions, normalization, evidence
eligibility, classification, and serialization are separate focused modules. The browser
renders only server-produced methodology results; JavaScript contains no scoring formula.

The existing current-session candidate store remains authoritative for candidate identity
and session history. Methodologies are projections over a candidate snapshot and never
delete, reorder, or mutate the stored candidate set. Frozen Research and canonical Phase 3A
remain distinct from the experimental profiles.

## Methodologies

### Legacy Prime Setup

`LEGACY PRIME SETUP — HISTORICAL REFERENCE` evaluates exactly:

- price from $2 through $20;
- today's percentage change at least 10%;
- relative volume at least 5;
- short-interest percentage at least 5%.

Only exact canonical concepts with compatible units and point-in-time eligibility count.
If any input is absent or semantically different, the result is `UNEVALUABLE`. A Finviz
Short Float snapshot is not silently substituted for published short interest, and a
non-daily return is not silently substituted for today's percentage change.

### Peer Reference Methodology

`PEER REFERENCE METHODOLOGY — NOT OUR MODEL` exposes the described variables, weights, and
Prime thresholds. It does not calculate Pressure, Ignition, Prime, or Subprime because the
reference did not specify every normalization, estimated-SI formula, float multiplier
application rule, TTM Squeeze implementation, Subprime formula, or missing-data policy.
The result is `REFERENCE DEFINITION INCOMPLETE`, with the exact missing definitions listed.

### Adam Evidence-Gated Prime v1

The complete preregistered policy is in
`docs/batch-14-independent-prime-methodology-plan.md`. Its dimensions are Pressure,
Ignition, and Evidence Coverage. Component values may be displayed when provider data is
available, but only research-admissible values support a dimension score or classification.

Missing components are never converted to zero. A partial dimension score is computed only
when at least 70% of its component weight is supported and its critical domains are present.
The score is then the explicitly coverage-qualified weighted mean over supported components.
Below that gate the score is withheld rather than extrapolated from one field.

## Candidate visibility and comparison

All discovered candidates remain represented by default, including `NOT QUALIFIED` and
`UNEVALUABLE`. Display filters operate on a copy of the row list and never alter session
state. Every candidate detail contains a comparison table with:

`Methodology`, `Pressure`, `Ignition`, `Coverage`, `Classification`, `Evaluable?`,
`Supporting Evidence`, `Missing Evidence`, and `Reason`.

Sorting is stable, supports both directions, and always places missing values last. The
comparison page supports Pressure, Ignition, Coverage, classification, percentage change,
relative volume, float, short float, and freshness.

## Visualization

The reliable deployment target is a dependency-free two-dimensional SVG scatter plot:

- X: Pressure;
- Y: Ignition;
- point size and opacity: Evidence Coverage;
- color: classification.

Hover reveals symbol, classification, provider status, dimension values, percentage
change, and relative volume. Filters and selected table rows synchronize with the chart.
Candidates without numeric dimensions remain in the table and are listed as unplotted;
they are never assigned artificial coordinates.

## Application and provider modes

- `LOCAL_FULL`: local-only bind, private provider file permitted, IBKR Gateway may be used.
- `CLOUD_PROVIDER_MODE`: bind `0.0.0.0:$PORT`; environment variables only; IBKR unavailable
  unless a separately authorized remote Gateway is explicitly configured.
- `FROZEN_DEMO`: deterministic, network-free, committed sanitized aggregate data.

The deployment image contains no `.private` file, token, cookie, password, authenticated
URL, raw provider response, private raw bar, or local filesystem path. Finviz, NewsAPI,
Finnhub, and SEC remain optional field-level providers. Provider unavailability is
reported, never replaced globally by another provider.

## Frozen cloud data

Railway uses a committed sanitized frozen-demo aggregate containing the 13 candidate
identities, rule outcomes, explanations, and totals needed by the dashboard. It contains
no raw OHLCV, forward window, provider credential, private evidence ID, machine path, or
outcome data. It is labeled `FROZEN_DEMO`, not represented as the private canonical tree,
and must reproduce exactly `97 PASS / 20 FAIL / 208 UNKNOWN`.

## API and deployment

The server retains existing routes and adds stable aliases:

- `/health`, `/api/health`;
- `/ready`, `/api/readiness`;
- `/api/providers`;
- `/api/frozen/candidates`, `/api/frozen/candidate/<symbol>`;
- `/api/current/candidates`, `/api/current/candidate/<symbol>`;
- `/api/current/refresh`, `/api/discovery/refresh`;
- `/api/methodologies`, `/api/methodologies/<symbol>`;
- `/api/export`.

Responses use a versioned envelope and contain no secrets. `/health` proves the process can
serve requests. `/ready` proves the selected frozen source loaded and the application is
operational while reporting optional provider capability states; missing IBKR does not
make cloud readiness fail.

Railway uses a root `Dockerfile`, `railway.toml`, `PORT`, a production start command, and a
configured health-check path. The server binds `0.0.0.0` only in cloud mode and preserves
`127.0.0.1:8787` locally. Railway variables are configured through the platform's variable
mechanism and only their names are documented.

## Error and conflict handling

Unsupported units, stale inputs, point-in-time ineligibility, provider disagreement, and
missing fields are structured evidence states. Material conflicts produce `CONFLICTED`
before any threshold classification. Optional provider faults are isolated per provider
and sanitized. No exception response includes credentials or local filesystem paths.

## Testing and verification

All feature work follows red-green-refactor. Tests use deterministic synthetic provider
fixtures and the existing external-network guard. No normal test loads private config or
calls a provider. Coverage includes methodology separation, missingness, classifications,
candidate preservation, sorting, visualization schema, all deployment modes, `PORT`,
health/readiness, stable API schemas, secret redaction, frozen totals, canonical Phase 3A
integrity, registry integrity, and the no-account/no-order boundary.

Final verification uses one complete pytest run with `-p no:cacheprovider`, a fresh
`--basetemp`, and `--junitxml`. Reported totals come from parsed XML. Git diff checks,
staged-secret scanning, private-artifact verification, frozen verification, archive
verification, and public Railway smoke tests follow.

## Explicit exclusions

TTM Squeeze is `NOT IMPLEMENTED` unless a later focused task can define and test a
canonical completed-bar implementation without delaying P0. There is no backtest, outcome
optimization, Phase 3E work, automated trading, account access, order access, insecure
Gateway tunnel, or predictive-validity claim.
