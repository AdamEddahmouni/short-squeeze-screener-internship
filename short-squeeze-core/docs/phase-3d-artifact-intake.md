# Phase 3D Artifact Intake

The offline intake layout separates `plans`, `raw`, `manifests`, `normalized`, `review`, `curated`, and `rejected` content. Commands accept exact manifest paths and never recursively discover files.

Each raw record carries a stable relative path, media type, byte length, SHA-256, provenance ID, source and fixture classifications, capture method, point-in-time timestamps, content status, and sensitive-content status. Absolute paths never affect identity. Verification reads bytes only; normalization writes a separately classified derived artifact and never modifies its source.

Missing files, mismatched hashes or lengths, unsupported media, duplicate IDs, and restricted content are explicit review results. Source artifacts are not repaired, rewritten, or deleted by the deterministic runtime.
