# Phase 3D Acquisition Plan Policy

`phase_3d_acquisition_plan_policy.v1` freezes the research question, population, fixed date range, source definitions, sample bounds, source-order sampling, unique-security deduplication, artifact requirements, substitution rules, and all downstream policy versions before outcome review. Only `PREREGISTERED` and `ACTIVE` plans can produce included cases. `DRAFT`, `CLOSED`, and `SUPERSEDED` plans remain reviewable but cannot curate an included case.

Plan identity uses semantic criteria only. The informational creation timestamp is serialized for context but excluded from identity. Changing any criterion creates a new UUIDv5 identity; it never silently revises the old plan.

The committed pilot targets up to 20 US-listed common-stock attempts from one explicit historical event-feed export during a fixed 2024 period. It is outcome-blind and source-defined. A small or empty complete cohort is valid; every attempted and excluded case remains in the ledger.
