# Phase 3C Boundary Selection Policy

`earliest_detection_boundary_per_symbol.v1` groups rows by symbol and selects the minimum `(evaluation_as_of, case_id)`. It uses no detection result, outcome label, return, maximum move, or classification. Equal timestamps are fully resolved by canonical case ID; ambiguity is reserved for missing or unresolved boundary data.

`all_case_boundaries.v1` preserves every eligible boundary. It is appropriate for case descriptions, but repeated-symbol observations are labeled dependent and do not become independent samples.
