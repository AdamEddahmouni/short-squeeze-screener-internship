# Phase 3D Outcome Leakage Prevention

The plan, boundary, Phase 3A request, and Phase 3A result must be serialized and frozen before outcome capture. Discovery/evaluation and outcome manifests must differ. Eligibility, identity, missingness, provider substitution, boundary selection, and Phase 3A input fields are scanned for outcome content.

Each freeze stage is audited independently against the outcome capture time. An outcome captured before the plan freeze emits `OUTCOME_ARTIFACT_CAPTURED_BEFORE_PLAN_FREEZE`, before the boundary freeze emits `OUTCOME_ARTIFACT_CAPTURED_BEFORE_BOUNDARY_FREEZE`, and before either the Phase 3A request or result freeze emits `OUTCOME_ARTIFACT_CAPTURED_BEFORE_EVALUATION_FREEZE`.

The audit reports the exact required diagnostics for prohibited input flow, early outcome capture, outcome-aware or maximum-return selection, post-event discovery sourcing, and plan mutation after outcome access. A passed audit emits `LEAKAGE_AUDIT_PASSED`. Any other diagnostic emits `LEAKAGE_AUDIT_FAILED`, blocks empirical publication, returns a nonzero audit command status, and retains the case attempt.
