# Batch 04 — Preflight Contract

`preflight_contract_version = phase_3d_submission_kit_preflight.v1`
Schema version: `1.0.0` (unchanged).

## Purpose

Preflight validates a local bundle offline and emits a deterministic
`PreflightReport`. It is preparation and validation only. It performs no network
access, no credential access, no case association, and no outcome work.

## Ordered steps

1. locate the local bundle root;
2. validate the manifest (`IntakeManifest` model validation on load);
3. inspect the raw artifact bytes;
4. verify SHA-256 and byte length (`validate_artifact_bytes`);
5. validate the mapping profile (`ColumnMappingProfile` model validation on load);
6. parse and normalize supported bars (`normalize_from_bytes`);
7. produce deterministic diagnostics (`NormalizationDiagnostics`);
8. produce the deterministic `PreflightReport`;
9. stop before any case association.

## Statuses

| Status | Condition |
| --- | --- |
| `READY_FOR_FUTURE_ASSOCIATION` | Artifact ACCEPTED and normalization ACCEPTED. |
| `NOT_READY_QUARANTINED` | Normalization QUARANTINED (some rows collapsed/quarantined). |
| `NOT_READY_REJECTED` | Artifact REJECTED or normalization REJECTED. |

`ready_for_case_association` is true only when the status is
`READY_FOR_FUTURE_ASSOCIATION`.

## What `READY_FOR_FUTURE_ASSOCIATION` does NOT mean

It means only that the local bundle passed the current intake and normalization
checks. It does **not** mean the data is accurate, the provider license is legally
sufficient, a particular historical case is covered, the outcome window is complete,
that Phase 3A can run, that Phase 3B can publish, or that anything is predictively
validated.

## Report fields

The report carries: `schema_version`, `preflight_contract_version`, `bundle_id`,
`artifact_id`, `profile_id`, `status`, `reason_codes`, `artifact_sha256`,
`artifact_byte_length`, `provider_name`, `provider_product_or_export_name`,
`user_entitlement_assertion`, `retrieval_time`, `export_time`, `canonical_symbol`,
`provider_symbol`, `market_or_venue`, `bar_interval`, `event_timezone`,
`timestamp_semantics`, `session_coverage`, `price_adjustment_semantics`,
`volume_adjustment_semantics`, `expected_start_time`, `expected_end_time`,
`observed_start_time`, `observed_end_time`, `normalized_bar_count`,
`rejected_row_count`, `quarantined_row_count`, `diagnostic_count`,
`ready_for_case_association`, and five constant-false booleans:
`case_association_performed`, `outcome_capture_performed`,
`phase_3a_records_created`, `phase_3b_records_created`, `phase_3e_started`.

- `observed_start_time` / `observed_end_time` are explicit nulls when no bars are
  normalized.
- Retrieval time, export time, and event times are kept as distinct concepts.
- No absolute local path enters the report or its deterministic identity.
- The report's `deterministic_id` is a UUIDv5 over its canonical content.

## Case-association boundary

The preflight functions accept only `(root|content, manifest, profile)`. There is
no parameter through which a case id, boundary id, known-id set, or outcome could be
supplied. Case association remains the non-executing Batch 03 boundary and is out of
scope for this batch.
