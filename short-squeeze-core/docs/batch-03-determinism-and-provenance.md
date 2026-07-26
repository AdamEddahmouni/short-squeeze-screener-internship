# Batch 03 — Determinism and Provenance

## Determinism guarantees

- Identity uses UUIDv5 via `deterministic_acquisition_id` (namespace-scoped
  canonical JSON). The canonicalizer drops non-identity keys
  (`absolute_path`, `informational_created_at`, `deterministic_id`), so no
  absolute path and no wall-clock value can enter an identity.
- Canonical serialization uses the repository encoder
  (`squeeze_core.serialization.canonical_json_bytes`): sorted keys, `,`/`:`
  separators, UTF-8, exact `Decimal` strings, explicit nulls, `allow_nan=False`.
- Stable ordering everywhere: bars by `(event_start_time, source_row_number)`,
  reason codes and row diagnostics sorted, artifact/field order stable.
- LF line endings for every generated document; `.gitattributes` enforces
  `eol=lf` (and `*.jsonl eol=lf`), so committed fixtures cannot pick up CRLF —
  the Batch 01 CRLF/hash defect is not repeated.
- No random IDs, no `uuid1`/`uuid4`, no `getenv`, no `today`/`utcnow`, no
  network, database, ML, or dataframe imports anywhere in the acquisition
  package. The acquisition isolation guard (`tests/acquisition/test_isolation.py`)
  enforces this across the new package.

## Twice-run byte comparison

`build_batch03_documents()` is pure over in-memory synthetic bytes with fixed
instants; repeated builds are byte-identical (`test_batch03.py`). The generator
script writes the same bytes to the gitignored `build/acquisition/batch-03/`,
and all five CLIs are byte-identical across repeated runs and match the committed
fixtures (`test_batch03_cli.py`).

## Provenance separation

The workflow keeps these distinct at all times:

1. raw local source artifact (bytes never modified);
2. user-supplied intake declaration (manifest);
3. artifact validation;
4. parsing profile;
5. normalized canonical bars;
6. case association (declaration + reference validation only).

`retrieval_time`, `export_time`, and bar event times are separate concepts and
are surfaced separately in the intake summary. Every canonical bar records
`source_artifact_id`, `source_row_number` (physical line), and `source_record_id`
so its origin is traceable after any allowed sorting. No outcome value enters any
pre-outcome identity, and items 7 (outcome capture) and 8 (Phase 3B publication)
are not performed in this batch.

## Anchors

`determinism-anchors.json` records the deterministic id of every identity-bearing
model plus content hashes of the contract, normalized bars (JSONL + CSV), and
rejected-examples document. Anchors are unique 64-hex digests
(`test_batch03.py`).
