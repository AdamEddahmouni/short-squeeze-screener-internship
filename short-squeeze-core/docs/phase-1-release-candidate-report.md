# Phase 1 Compatibility Release-Candidate Report

## Repository state

- Repository: `short-squeeze-core`
- Branch: `phase/1-release-candidate-audit`
- Base (Phase 1I tip, unchanged): `b2cf674498aa2f5449c56a12674aee5e6451e1b4`
- Remotes: none · Push status: not pushed · Merge status: not merged
- Working tree: clean after commits
- Local tag: `phase-1-rc1` (annotated, local-only) created at finalization if all checks pass

## Baseline and final verification

| | Command | Result |
| --- | --- | --- |
| Baseline | `python -m pytest` (fresh basetemp) | 584 passed, 1 skipped, 0 failed |
| Final | `python -m pytest` (fresh basetemp) | 667 passed, 1 skipped, 0 failed |
| Dedicated audit | `python -m pytest tests/compatibility` | 90 passed |
| Determinism | Phase 1G/1H/1I artifacts regenerated ×2 | byte-identical, equal to committed anchors |

The single skip is the established IANA timezone-database portability skip. The 83 added tests are
all in `tests/compatibility/`.

## Audit findings

| ID | Severity | Domain | Evidence | Impact | Resolution | Tests | Remaining risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-1 | INFORMATIONAL | Tooling/env | `pyproject.toml` `--basetemp=.pytest-tmp` collides with pre-existing OS-locked `.pytest-tmp` (restrictive ACLs from an earlier runtime); bare `pytest` fails during cleanup with `WinError 5` | Bare documented command fails on this host only | Documented workaround (`--basetemp=.pytest-run-*`, gitignored); `pyproject.toml` intentionally not mutated | n/a | none on clean checkout |
| F-2 | INFORMATIONAL | Fixtures | Fixture-metadata schema differs across phases (inline origins vs `families` vs `allowed_origins`) | None — all honest and classified in-range | Provenance test is shape-tolerant; convergence deferred to preserve anchors | `test_phase_1_fixture_provenance.py` | none |
| F-3 | INFORMATIONAL | Architecture | Adapters share conceptually similar timestamp/date-only/decimal/raw-hash/diagnostic logic | None functionally; potential future drift | Documented as intentional/deferred; not refactored because behaviors are not provably identical and any refactor risks changing anchors | existing per-adapter suites | low, monitored |

No BLOCKER, HIGH, MEDIUM, or LOW findings. **The audit found no correctness defect requiring a
code change.** The Phase 1 evidence foundation is internally coherent, backward-compatible,
deterministic, isolated, and documented. All release-candidate additions are audit infrastructure
(a centralized anchor manifest, compatibility/PIT/lifecycle/provenance/isolation/CLI/matrix tests,
and documentation) — no runtime behavior was modified.

## Canonical compatibility

- **Schema version:** `1.0.0` remains the only accepted version; a non-`1.0.0` version fails
  validation.
- **Observation-envelope changes:** none.
- **Payload changes:** none in this branch. Phase 1I's relaxations were validated, not altered.
- **Backward compatibility:** old serialized observations (committed jsonl fixtures) still
  validate; serialize→deserialize round-trips are equal; repeated serialization is byte-identical
  and hashes are stable.
- **Trade-size relaxation:** `TradePayload.size` is `int | None`; missing size (`None`) serializes
  distinctly from `0`. Confirmed by `test_missing_trade_size_is_distinct_from_zero`.
- **Crossed-quote relaxation:** `QuotePayload.is_crossed` is objective structure; a crossed quote
  with `KNOWN_VALUE` quality validates and is not forced to `INVALID`. Confirmed by
  `test_crossed_quote_is_representable_without_forcing_invalid`.
- **Hash impact:** none. Every retained Phase 1G/1H/1I anchor is unchanged (see the anchor
  manifest). Newly added policy/bundle fields use pydantic `exclude`/`exclude_if` so existing
  serialized bytes and hashes are preserved.

## Domain coverage

All ten domains pass every audit dimension:

| Domain | Contract | Availability | Lifecycle | Dup/Conflict | Fixture | CLI | Docs | Isolation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CANDIDATE_SNAPSHOT | ✅ | ✅ | n/a (point) | ✅ | ✅ | ✅ | ✅ | ✅ |
| BORROW_FEE | ✅ | ✅ | n/a (point) | ✅ | ✅ | ✅ | ✅ | ✅ |
| BORROW_AVAILABILITY | ✅ | ✅ | n/a (point) | ✅ | ✅ | ✅ | ✅ | ✅ |
| PUBLISHED_SHORT_INTEREST | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SEC_FILINGS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| TRADING_HALTS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| NEWS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MARKET_BARS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| TRADES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| QUOTES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Deterministic anchors

Every Phase 1G/1H/1I anchor listed in the handoff is present, centralized in
`tests/fixtures/compatibility/phase_1_anchor_manifest.json`, cross-checked against the committed
per-phase metadata, and re-verified by twice-repeated regeneration. **No anchor changed.** Full
values are in [`phase-1-deterministic-anchor-manifest.md`](phase-1-deterministic-anchor-manifest.md).

## Fixture provenance

Every fixture family is classified within {`SANITIZED_RECORDED_SAMPLE`,
`SANITIZED_REPRESENTATIVE_SAMPLE`, `SYNTHETIC_EDGE_CASE`}. No `SANITIZED_RECORDED_SAMPLE` is
currently used and every metadata file records `recorded_sample_found: false`, so no representative
sample is overstated as recorded. No credentials, account identifiers, emails, live/routable URLs,
or environment-specific absolute paths exist; all URLs use `.invalid` hosts. Details in
[`phase-1-fixture-provenance-audit.md`](phase-1-fixture-provenance-audit.md).

## CLI inventory

Eight commands (`validate`, `replay`, `normalize-provider`, `build-evidence`,
`build-evidence-timeline`, `build-halt-state`, `build-bar-series`, `build-trade-quote-series`),
all local, offline, deterministic, nonzero-on-invalid, and free of scoring/ranking/recommendation
output. Details in [`phase-1-cli-inventory.md`](phase-1-cli-inventory.md).

## Architecture-consistency assessment

Duplication exists across adapters (timestamp/date-only policies, decimal/int parsing, raw
hashing, diagnostic ordering, revision linking, conflict identity, age calculation). Per the audit
criteria, a shared abstraction is introduced only when behavior is provably identical, tests prove
compatibility, hashes are unchanged, and provider-specific differences are preserved. Those
conditions are not met — provider timestamp/date-only and unit semantics differ in intentional
ways, and any consolidation risks changing anchored hashes. The duplication is therefore recorded
as **intentional/deferred** (finding F-3), not refactored in this compatibility release candidate.

## Files changed (grouped)

```
docs/
  phase-1-audit-plan.md
  phase-1-evidence-domain-matrix.md
  phase-1-evidence-domain-matrix.json
  phase-1-lifecycle-consistency.md
  phase-1-fixture-provenance-audit.md
  phase-1-cli-inventory.md
  phase-1-deterministic-anchor-manifest.md
  phase-1-known-limitations.md
  phase-1-release-candidate-checklist.md
  phase-1-release-candidate-report.md
tests/fixtures/compatibility/
  phase_1_anchor_manifest.json
tests/compatibility/
  __init__.py
  test_phase_1_anchor_manifest.py
  test_phase_1_release_candidate.py
  test_phase_1_lifecycle.py
  test_phase_1_fixture_provenance.py
  test_phase_1_isolation.py
  test_phase_1_cli_inventory.py
  test_phase_1_domain_matrix.py
```

No files under `src/` were modified. No existing fixtures were modified.

## Deviations from the handoff

- The audit added `tests/compatibility/` and a compatibility fixture directory rather than a single
  runner file, splitting the required checks into focused modules per the "follow existing
  repository conventions" guidance. All handoff-required test locations are represented.
- `pyproject.toml` was intentionally **not** changed for finding F-1 (environment-specific temp-dir
  lock); the workaround is documented instead. This is the conservative choice for a compatibility
  audit and preserves the handoff's expected invocation semantics on a clean checkout.

## Remaining limitations

This release candidate still contains **no** live integrations, streaming, database, GUI, alerts,
indicators, derived metrics, scoring, ranking, recommendations, backtesting, paper trading, or live
trading. See [`phase-1-known-limitations.md`](phase-1-known-limitations.md).

## Release-candidate decision

**Phase 1 compatibility release candidate approved.**

## Recommended next phase

Begin Phase 2A by specifying and implementing deterministic derived market metrics from
point-in-time market-bar evidence, starting with return, gap, range, and volume-baseline contracts
while preserving strict no-look-ahead behavior and without introducing squeeze scoring, ranking,
recommendations, or live integrations. (Not started in this session.)
