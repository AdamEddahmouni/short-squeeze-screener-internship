# Phase 1 Evidence-Foundation Audit Plan

Branch: `phase/1-release-candidate-audit`
Starting HEAD (Phase 1I tip): `b2cf674498aa2f5449c56a12674aee5e6451e1b4`
Baseline suite verified: **584 passed, 1 skipped, 0 failed** (the single skip is the IANA
timezone-database portability skip).

This plan is committed **before** any implementation change, per the audit-first requirement.
Its purpose is to determine whether the completed Phase 1 foundation is internally coherent,
backward-compatible, deterministic, documented, isolated, and ready to become a local
compatibility release candidate. No new provider domain, derived metric, scoring, ranking,
live integration, or strategy logic is in scope.

## 1. Scope and non-goals

In scope: repository-wide audit of the ten Phase 1 evidence domains, their canonical contracts,
point-in-time eligibility rules, lifecycle/duplicate/conflict semantics, fixture provenance,
deterministic anchors, CLI surfaces, documentation, and isolation guarantees; plus minimal,
backward-compatible fixes for any defects the audit proves.

Explicitly out of scope (must not be started): derived metrics, scoring, ranking,
recommendations, live/streaming providers, databases, GUI/web, alerts, paper/live trading,
indicators (RSI/MACD/Bollinger/Keltner/TTM/ATR/etc.), order-flow, aggressor inference, spread
analytics, synthetic NBBO, sentiment, catalyst classification, and any Phase 2 work.

## 2. Evidence domains under audit

| Domain | Event type | Payload | Phase |
| --- | --- | --- | --- |
| CANDIDATE_SNAPSHOT | MARKET_SNAPSHOT | MarketSnapshotPayload | 1C |
| BORROW_FEE | BORROW_FEE | BorrowFeePayload | 1B |
| BORROW_AVAILABILITY | BORROW_AVAILABILITY | BorrowAvailabilityPayload | 1B |
| PUBLISHED_SHORT_INTEREST | PUBLISHED_SHORT_INTEREST | PublishedShortInterestPayload | 1D |
| SEC_FILINGS | SEC_FILING | SecFilingPayload | 1E |
| TRADING_HALTS | TRADING_HALT | TradingHaltPayload | 1F |
| NEWS | NEWS_ITEM | NewsItemPayload | 1G |
| MARKET_BARS | BAR | BarPayload | 1H |
| TRADES | TRADE | TradePayload | 1I |
| QUOTES | QUOTE | QuotePayload | 1I |

Note the terminology mapping: the coverage domain `CANDIDATE_SNAPSHOT` is carried by the
canonical event type `MARKET_SNAPSHOT` (`CoverageDomain.CANDIDATE_SNAPSHOT` ↔
`EventType.MARKET_SNAPSHOT`). This is deliberate and documented in the domain matrix.

## 3. Audit workstreams

1. **Canonical contract audit.** Confirm schema `1.0.0` is the only accepted version; confirm the
   observation envelope, payload bindings, Decimal/timestamp normalization, deterministic
   UUIDv5 identity, canonical JSON/JSONL key and list ordering, and raw-hash behavior are
   unchanged. Validate the Phase 1I relaxations explicitly: `TradePayload.size` nullable
   (missing ≠ zero) and crossed quotes representable without forcing `INVALID`. Prove old
   serialized observations still validate and old hashes are unchanged.
2. **Point-in-time policy audit.** Confirm every domain shares the rule: eligible only when
   provider/public availability ≤ `as_of` **and** local receipt ≤ `as_of` **and** effective time
   ≤ `as_of` (trades/quotes additionally gate non-future event time). Confirm event time alone
   never creates eligibility, and corrections/cancellations after `as_of` never mutate earlier
   bundles. Add cross-domain availability tests.
3. **Lifecycle audit.** Confirm observations are immutable, later records never mutate earlier
   ones, historical bundles are byte-stable, explicit revision/correction/cancellation/withdrawal
   links are preserved, and missing links are diagnosed. Build a cross-domain lifecycle matrix.
4. **Duplicate & conflict audit.** Confirm no domain averages sources, silently picks a winner,
   overwrites changed content, converts missing evidence into neutral evidence, or treats
   temporal differences as direct conflicts. Confirm deterministic conflict IDs and ordering.
5. **Fixture-provenance audit.** Confirm every fixture family carries exactly one allowed
   provenance class (`SANITIZED_RECORDED_SAMPLE`, `SANITIZED_REPRESENTATIVE_SAMPLE`,
   `SYNTHETIC_EDGE_CASE`); confirm no credentials, account identifiers, private/live/tracking
   URLs, or environment-specific absolute paths; confirm metadata matches contents. Produce a
   provenance report.
6. **Deterministic-anchor audit.** Centralize every retained anchor (Phase 1G/1H/1I plus fixture
   content hashes) in one machine-readable manifest and one compatibility test. Regenerate
   artifacts at least twice and prove byte identity. Do not rewrite anchors.
7. **CLI audit.** Inventory every command; confirm local-only, offline, deterministic JSON output,
   nonzero exit on invalid input, no credentials/network/database/GUI, and no strategy wording.
8. **Documentation audit.** Reconcile docs with code for schema, event/payload types, timestamp
   meanings, availability policies, coverage/lifecycle states, ages, duplicate/conflict behavior,
   fixture provenance, CLI usage, known limitations, and determinism guarantees. Historical
   completion reports are not rewritten.
9. **Isolation & security audit.** Scan `src/` for network/DB/GUI/web/ML clients, credential/token
   reads, wall-clock, random identity, pandas/numpy, indicators, and strategy/scoring/ranking
   language. Distinguish executable paths from documentation/enum labels.
10. **Architecture consistency audit.** Identify duplicated adapter logic (timestamp/date-only
    policies, decimal/int parsing, raw hashing, diagnostic ordering, revision linking, conflict
    identity, age calculation). Only abstract when behavior is truly identical, tests prove
    compatibility, hashes are unchanged, and provider-specific differences are preserved.
    Otherwise document duplication as intentional or deferred.

## 4. Deliverables

- `docs/phase-1-audit-plan.md` (this file).
- `docs/phase-1-evidence-domain-matrix.md` + machine-readable manifest.
- `docs/phase-1-lifecycle-consistency.md`.
- `docs/phase-1-fixture-provenance-audit.md`.
- `docs/phase-1-cli-inventory.md`.
- `docs/phase-1-deterministic-anchor-manifest.md`.
- `docs/phase-1-known-limitations.md`.
- `docs/phase-1-release-candidate-checklist.md`.
- `docs/phase-1-release-candidate-report.md`.
- `tests/fixtures/compatibility/phase_1_anchor_manifest.json` (machine-readable anchors).
- `tests/compatibility/test_phase_1_release_candidate.py` and companion audit tests.

## 5. Guardrails

- Confine all changes to `short-squeeze-core`. Never modify archived repositories
  (`0897562e05d75b812dd284de81dfafdfa1dea916`, `6dbefd1a6b271bfc48106c4aa002f211735551cd`,
  `84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8`) — read-only inspection only.
- Do not change schema `1.0.0` unless a breaking incompatibility is proven; stop and report first.
- Do not update an anchor because a test fails — investigate and explain any mismatch.
- No remotes, no push, no merge. Optional local annotated tag `phase-1-rc1` only if the full audit
  passes with a clean working tree.
- Note: the repository's configured pytest `--basetemp=.pytest-tmp` collides with a pre-existing
  OS-locked `.pytest-tmp` directory (restrictive ACLs from an earlier tool run). Audit runs pass
  `--basetemp=.pytest-run-audit-*` (already gitignored) to avoid the lock; this is an environment
  workaround only and changes no test logic.

## 6. Sequence

Audit plan → anchor manifest + compatibility test → cross-domain PIT tests → lifecycle/duplicate/
conflict tests → fixture-provenance + isolation tests → CLI compatibility tests → minimal fixes →
documentation reconciliation → RC report → final verified commit → optional local tag.
