# Batch 04 — Submission Kit Architecture

The submission kit is a thin, deterministic operator layer over the completed
Batch 03 `local_bar_intake` package. It adds no new intake semantics: it reuses the
Batch 03 models, enums, reason codes, CSV adapter, and normalization unchanged.

## Package

`src/squeeze_core/acquisition/historical_data_submission_kit/`

| Module | Responsibility |
| --- | --- |
| `synthetic.py` | The self-contained synthetic-valid example bundle (fictional provider `DEMO_FIXTURE_FEED`, symbol `ZZQ1`, venue `DEMO_VENUE_X`, six 5-minute UTC bars). |
| `templates.py` | Blank fill-in templates for the manifest, mapping profile, and (future-only) case association. Each contains every model field with `<REPLACE: ...>` placeholders and a `_field_guidance` block. |
| `preflight.py` | `PreflightStatus`, the `PreflightReport` model, `run_preflight` / `run_preflight_from_bytes`, and the offline `hash_file` tool. |
| `troubleshooting.py` | Reason-code guidance (`build_troubleshooting_index`) and the deterministic `build_invalid_scenario_index`. |
| `checklist.py` | The final operator checklist items and `build_operator_checklist`. |
| `documents.py` | Deterministic operator-facing prose (README, guides, rendered troubleshooting and checklist). |
| `kit.py` | `build_submission_kit` (operator kit files) and `build_batch04_fixtures` (committed canonical fixtures), plus the submission-kit manifest, determinism anchors, and fixture metadata. |

## Data flow

```
raw bytes + IntakeManifest + ColumnMappingProfile
        │
        ▼  (Batch 03, unchanged)
validate_artifact_bytes ──► ArtifactValidationReport
normalize_from_bytes ─────► NormalizationOutcome (NormalizedBarSet, NormalizationDiagnostics)
        │
        ▼  (Batch 04)
run_preflight_from_bytes ─► PreflightReport (readiness status + provenance echo)
```

Preflight never reaches steps beyond normalization. There is no code path from a
`PreflightReport` to a case association, an outcome, or any later-phase record.

## Surfaces

- Library: `run_preflight`, `run_preflight_from_bytes`, `hash_file`, the builders.
- CLI: `submission-kit-generate`, `historical-bar-hash`, `historical-bar-preflight`,
  `historical-bar-preflight-report`.
- Generator: `scripts/generate_batch04_submission_kit.py`.

## Outputs

- Operator kit: `operator-kits/historical-market-bars/` (guides, templates, examples).
- Canonical fixtures: `tests/fixtures/acquisition/batch04/` (regenerated exactly).

Both are pure functions of in-memory synthetic bytes with fixed instants; there is
no wall-clock, network, disk-order, or machine-path input to any committed byte.
