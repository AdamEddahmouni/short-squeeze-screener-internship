# Phase 1 Compatibility Release-Candidate Checklist

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Work on `phase/1-release-candidate-audit` | ✅ | branch created from Phase 1I tip `b2cf674` |
| 2 | Starting Phase 1I history intact | ✅ | `phase/1i-offline-trades-quotes` still at `b2cf674` |
| 3 | Archived repositories unchanged | ✅ | read-only inspection only; no reset/checkout/commit |
| 4 | Full baseline passes | ✅ | 584 passed, 1 skipped (with fresh basetemp) |
| 5 | All ten Phase 1 domains audited | ✅ | domain matrix + per-domain records |
| 6 | Domain matrix exists (human + machine) | ✅ | `phase-1-evidence-domain-matrix.{md,json}` |
| 7 | Lifecycle consistency matrix exists | ✅ | `phase-1-lifecycle-consistency.md` |
| 8 | Fixture provenance audited | ✅ | `phase-1-fixture-provenance-audit.md` + provenance tests |
| 9 | CLI surfaces audited | ✅ | `phase-1-cli-inventory.md` + CLI compat tests |
| 10 | Documentation reconciled with code | ✅ | matrix/anchor/CLI docs cross-checked by tests |
| 11 | Existing anchors centralized and verified | ✅ | `phase_1_anchor_manifest.json` + anchor test |
| 12 | Repeated generation byte-identical | ✅ | anchor + lifecycle determinism tests |
| 13 | Point-in-time policies coherent | ✅ | cross-domain PIT test across all ten domains |
| 14 | Canonical compatibility proven | ✅ | schema 1.0.0, round-trip, old fixtures validate |
| 15 | Phase 1I relaxations explicitly validated | ✅ | nullable size ≠ zero; crossed quote ≠ invalid |
| 16 | Isolation scans pass | ✅ | isolation test: no network/DB/GUI/ML/clock/random/strategy |
| 17 | No live or strategic behavior added | ✅ | additions are docs + tests only |
| 18 | Minimal fixes tested | ✅ (none required) | audit found no correctness defect; see report |
| 19 | Full suite passes | ✅ | 667 passed, 1 skipped |
| 20 | Working tree clean after commits | ✅ | verified at finalization |
| 21 | No remotes added | ✅ | `git remote -v` empty |
| 22 | Nothing pushed | ✅ | no remotes exist |
| 23 | Nothing merged | ✅ | audit branch only |
| 24 | Schema `1.0.0` unchanged | ✅ | no breaking schema change |
| 25 | No derived-metric phase started | ✅ | Phase 2A not begun |

Local annotated tag `phase-1-rc1` is created only if all criteria above hold with a clean working
tree and green suite.
