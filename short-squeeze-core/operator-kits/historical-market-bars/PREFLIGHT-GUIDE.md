# Preflight Guide

Preflight validates a local bundle offline and produces a deterministic readiness
report. It runs these steps in a fixed order and then stops:

1. locate the local bundle;
2. validate the manifest;
3. inspect the raw artifact;
4. verify SHA-256 and byte length;
5. validate the mapping profile;
6. parse and normalize supported bars;
7. produce deterministic diagnostics;
8. produce a deterministic readiness report;
9. stop before any case association.

Preflight never touches the network, never reads credentials, never associates a
bundle with a case, never computes an outcome, and never creates any later-phase
record.

## Running it

```
squeeze-core historical-bar-preflight --root <bundle-root> \
    --manifest <bundle-root>/manifest.json \
    --profile <bundle-root>/profile.json \
    --output <bundle-root>/preflight-report.json
```

Exit code is 0 when the status is ready, 1 otherwise. Use
`historical-bar-preflight-report` to write the canonical report bytes for
archiving.

## Statuses

- `READY_FOR_FUTURE_ASSOCIATION` — artifact and normalization
  both accepted.
- `NOT_READY_QUARANTINED` — normalization quarantined some
  rows; review before relying on the bundle.
- `NOT_READY_REJECTED` — a barrier blocked the artifact or
  normalization; see the reason codes.

## What ready does NOT mean

`READY_FOR_FUTURE_ASSOCIATION` means only that the local bundle passed the current
intake and normalization checks. It does not mean the data is accurate, the
license is legally sufficient, a particular historical case is covered, an outcome
window is complete, that later analysis can run or publish, or that anything is
predictively validated.

## Report fields

The report records provenance, declared semantics, observed coverage, counts, and
an explicit `ready_for_case_association` flag. Five booleans
(`case_association_performed`, `outcome_capture_performed`,
`phase_3a_records_created`, `phase_3b_records_created`, `phase_3e_started`) are
always false in this batch. Unknown values are explicit nulls; no absolute path
appears in the report.
