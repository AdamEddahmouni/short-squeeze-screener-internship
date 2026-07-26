# Phase 3B Candidate Case Inventory

## Scope and evidence rule

This inventory covers the symbols named in the Phase 3B handoff (`BIYA`, `KLRS`,
`LBGJ`, `SG`, `TRVI`, and `SLS`) plus `KLOS`, which appears in the 2026-07-17
advisor transcript and conflicts with the `KLRS` spelling retained in the archived
application log. Discovery was read-only. The three archived repositories remained
clean at their required commits.

An archived provider request proves that the inherited application processed a
symbol, but it does not alone prove that the user interface surfaced the symbol.
`ORIGINAL_PLATFORM_SURFACED` is therefore used only where a meeting transcript,
retained Phase 2V detection record, or explicit archived handoff identifies a displayed
row. Absence from an artifact is never treated as proof that a symbol was not surfaced.

## Inventory

| Symbol / case | Case type | Case status | Platform status | Detection-time evidence | Evaluation inputs | Outcome data | Supporting artifacts | Next acquisition or limitation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BIYA_EARLIEST_BOUNDARY` | `ORIGINAL_PLATFORM_SURFACED` | `COMPLETE` | Surfaced | Defensible earliest boundary `2026-07-17T14:23:58Z` from the Phase 2V bounded detection record | Complete frozen Phase 3A request and result | Retained 24-hour observation crosses +25%; coverage is partial but the crossing is directly observed | `tests/fixtures/evaluation/biya_earliest_boundary_evaluation.json`; Phase 2V validation and outcome-amendment fixtures; archived `app.log`; advisor transcript | Original methodology and short-pressure inputs remain unavailable; movement does not establish squeeze causation |
| `BIYA_LATEST_BOUNDARY` | `ORIGINAL_PLATFORM_SURFACED` | `COMPLETE` | Surfaced | Defensible latest boundary `2026-07-17T16:54:58Z` from the Phase 2V bounded detection record | Complete frozen Phase 3A request and result | Retained 24-hour observation crosses +25%; coverage is partial but the crossing is directly observed | `tests/fixtures/evaluation/biya_latest_boundary_evaluation.json`; Phase 2V validation and outcome-amendment fixtures; archived `app.log`; advisor transcript | Original methodology and short-pressure inputs remain unavailable; movement does not establish squeeze causation |
| `KLRS_ARTIFACT_DISCOVERY` | `ORIGINAL_PLATFORM_SURFACED` | `ARTIFACT_DISCOVERY_ONLY` | Surfaced | No defensible exact detection time; bounded to the archived 2026-07-17 application run | Missing canonical point-in-time snapshot, metrics, and readiness inputs | Missing | Archived `app.log` repeatedly requests `KLRS`; `SQUEEZE_FORMULA_REDESIGN_HANDOFF.md` identifies `KLRS` as a real displayed row that day | Acquire a timestamped candidate snapshot, point-in-time inputs, and outcome series before evaluation |
| `LBGJ_ARTIFACT_DISCOVERY` | `ORIGINAL_PLATFORM_SURFACED` | `ARTIFACT_DISCOVERY_ONLY` | Surfaced | Meeting evidence bounds the display to the 2026-07-17 session but does not preserve the row timestamp | Missing canonical point-in-time snapshot, metrics, and readiness inputs | Only an approximate contemporaneous 13% value is discussed; no deterministic 24-hour observation exists | Advisor transcript explicitly says the system identified `LBGJ` as a Prime Setup; archived `app.log`; archived redesign handoff | Acquire timestamped evaluation inputs and a normalized outcome series; do not convert the quoted 13% into an outcome label |
| `SG_ARTIFACT_DISCOVERY` | `ORIGINAL_PLATFORM_STATUS_UNKNOWN` | `ARTIFACT_DISCOVERY_ONLY` | Unknown | No defensible detection time | Missing | Missing | Archived `app.log` contains repeated IBKR market-data requests for `SG` | A provider request does not prove a surfaced row; acquire a candidate row or UI artifact first |
| `TRVI_ARTIFACT_DISCOVERY` | `ORIGINAL_PLATFORM_STATUS_UNKNOWN` | `ARTIFACT_DISCOVERY_ONLY` | Unknown | No defensible detection time | Missing | Missing | Archived `app.log` contains repeated IBKR market-data requests for `TRVI` | A provider request does not prove a surfaced row; acquire a candidate row or UI artifact first |
| `SLS_ARTIFACT_DISCOVERY` | `ORIGINAL_PLATFORM_STATUS_UNKNOWN` | `ARTIFACT_DISCOVERY_ONLY` | Unknown | No defensible detection time | Missing | Missing | Archived `app.log` contains repeated IBKR market-data requests for `SLS` | A provider request does not prove a surfaced row; acquire a candidate row or UI artifact first |
| `KLOS_IDENTITY_CONFLICT` | `ORIGINAL_PLATFORM_SURFACED` | `BLOCKED_CONFLICTING_IDENTITY` | Surfaced under the transcript spelling | Meeting filename bounds the display to the 2026-07-17 session; no exact row timestamp survives | Missing; identity conflicts with `KLRS` in other artifacts | Missing | Advisor transcript explicitly says the system identified `KLOS`; reconstruction timeline repeats `KLOS`; archived log instead contains `KLRS` | Resolve whether `KLOS` and `KLRS` refer to distinct displayed rows or a transcription error before evaluation |

## Initial registered dataset

Only the two BIYA boundary cases qualify as complete historical research cases.
`KLRS` and `LBGJ` are retained as surfaced artifact-discovery cases. `SG`, `TRVI`,
and `SLS` retain unknown platform status. `KLOS` remains blocked by conflicting
identity evidence. These incomplete cases remain visible in registry and batch-quality
diagnostics, but they do not receive fabricated Phase 3A results or outcome labels.

Deterministic synthetic cases will cover every detection, outcome, and research
classification branch. They will be marked `SYNTHETIC_EDGE_CASE` and will never be
presented as historical evidence.

## Acquisition gap

Completing additional historical cases requires timestamped candidate rows, eligible
point-in-time evidence for the Phase 3A request, and normalized observations covering
the fixed 24-hour outcome horizon. Phase 3B does not perform broad market acquisition.
Any future acquisition must target an explicit registered case, preserve raw responses
and request metadata, normalize separately, and leave tests network-free.
