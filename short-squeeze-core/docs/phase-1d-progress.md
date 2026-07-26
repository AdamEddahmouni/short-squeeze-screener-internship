# Phase 1D Progress and Completion Record

## Starting state

- Starting branch: `phase/1c-offline-finviz-cross-source`
- Starting HEAD: `1363ac65a88774cc5124a700a6a88e3cc2483888`
- Phase 1D branch: `phase/1d-offline-finra-short-interest`
- Starting tree: clean
- Remotes: none
- Baseline: 146 tests passed

## Evidence result

No FINRA feed, file, parser, or recorded provider row was found. Phase 0 records the feed as not found. The archived mocked Yahoo metadata test supports representative field concepts only. Phase 1D consequently uses `SANITIZED_REPRESENTATIVE_SAMPLE` and `SYNTHETIC_EDGE_CASE` exclusively.

## Canonical compatibility

`PublishedShortInterestPayload` was sufficient. No canonical payload, envelope, enum, event binding, or schema change was made. Schema remains `1.0.0`. Existing Phase 1A, 1B, and 1C fixtures and hashes remain unchanged. Empty Phase 1D evidence metadata serializes away so the Phase 1C bundle and serialized-bundle hashes remain unchanged.

## Focused commits

- `fbaff68` design specification and test-first plan
- `a7ecdb0` FINRA-shaped provider model and parsers
- `c85e26e` offline normalizer and availability/revision ADRs
- `1333d61` publication eligibility, coverage, and ages
- `0994903` settlement-period conflict semantics
- `23f971d` representative/synthetic fixtures and replay timeline
- `66c3b93` local CLI normalization and timeline support
- `d253b90` fixture provenance and required-case verification

## Fixture hashes

| Artifact | SHA-256 |
|---|---|
| Complete FINRA-shaped raw record | `27534445d12eeea4e15ec32d4416a12de533e23f3dea30dce2384d548d07f583` |
| Original FINRA observation | `1a4a9bb9d3e7f79bfda2396bc724e6c743dd1e12b4760914cac7fd1ff29c7f70` |
| Correction FINRA observation | `fcfa4f7c1f901b2c2f6f99733c35673e1d87fea3dca756b0eb8a4d677be9a60e` |
| Mixed Phase 1D JSONL | `de24c62a4d964e4ff9a555a4357b9fc0a212430c2c5336f676cc61c0fe6fb5f0` |
| Strict replay | `2532dc3171da766e4fc9a631fd69a0fa8142462f3cd02e1b9f416073730380ff` |
| Before publication bundle | `7949a2b2ad188e3f113b6363bdb1a2a6e5ebff4c7aadc28b8c2da2de99474168` |
| After publication/before receipt bundle | `206b8d77fc0179bce2bae7639a4d50d80af76bc92f47fce191b1c01d1b7656c3` |
| After original receipt bundle | `20eaefbf02872e3209bc82a8df28b5d0723bcd253301ed634ab4289921a361bd` |
| Before correction receipt bundle | `3b891ae9ac5439bb4a639dab72ca6ca49e8e365d43ffa9b1cb0f746026feb9f0` |
| After correction receipt bundle | `667ae58af765655d637409864bd9786e1228d30c7e7832599d4078b64ba64c12` |
| Serialized after-correction bundle | `2d29dc529ea4cb83c7df486ecb5cc52beedacfe9bf71315a543be2dfddf99e3e` |

## Verification status

The implementation suite reached 224 passing tests before the documentation commit. Final fresh full-suite, CLI, determinism, isolation, archive, and Git verification is recorded in the completion report delivered from the final committed state.

## Boundaries

Phase 1D remains offline and strategy-neutral. It contains no FINRA download, daily short-volume normalization, live Finviz/IBKR access, database, GUI, score, candidate rank, recommendation, entry/exit logic, trading instruction, or Phase 1E work.
