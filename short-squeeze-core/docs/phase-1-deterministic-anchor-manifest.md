# Phase 1 Deterministic-Anchor Manifest

The authoritative machine-readable anchor list is
[`tests/fixtures/compatibility/phase_1_anchor_manifest.json`](../tests/fixtures/compatibility/phase_1_anchor_manifest.json).
It is verified by `tests/compatibility/test_phase_1_anchor_manifest.py`, which:

1. cross-checks every manifest anchor against the committed
   `expected_phase_1{g,h,i}_bundle_metadata.json` files;
2. regenerates the Phase 1G/1H/1I artifacts **twice** via the fixture builders and asserts the
   regenerated hashes are byte-identical across runs, equal to the committed metadata, and equal
   to the manifest;
3. re-verifies provider fixture content hashes and standalone fixture hashes.

No anchor is rewritten by the audit. Any mismatch is a failure to be investigated, not an update.

## Retained anchors

### Phase 1G (`observation_schema_version` 1.0.0)

| Anchor | SHA-256 |
| --- | --- |
| Mixed JSONL | `7eab70a7aac2526c2b76d8af4d7c6c246fb6738beabfc71b8075580e0a4e4001` |
| Strict replay | `8ac4ffb2e15ee2a4f19e6e6eb8320527cdbbd24f36d99261c007b14394d74aee` |
| Final bundle | `90ab29e174a258d5c873a0c12bf425297cb7ee8636ec369730837ab4a3153763` |
| Serialized final bundle | `b328c8789073f3bccc9dcb15e31fe776e40e7daf955ac87179f4b43e8859e2ec` |

### Phase 1H

| Anchor | SHA-256 |
| --- | --- |
| Partial observation | `474f3ebcf2a7ff65e931b60ae0e23eca4dc415f63f67f257c6b2c7c12b9aadfd` |
| Completed observation | `8004110b85fc8dbde14a905ba62110b2484e764c8c52b1001a661be8a944dc3a` |
| Corrected observation | `2a1d7f1359f1d09832a279be95aa819802506e2861af07746e81b37ae7fcbdcd` |
| Cancelled observation | `fde8a01f379ff7f5d0476ba72241d06769652da651640114774035fde384d5ab` |
| Mixed JSONL | `17a2be8548045e6234afbd5e5ccf7be4d298ed6eb18ab499e9762316eec96f64` |
| Strict replay | `95b367cb292593066412c5157b96d9c6b67113829a0ed0b8e3cf1144baf87652` |
| Final bar series | `219b568d777df52bc6e4288a932a5595779ff64579c7ccc0494936067a163952` |
| Final bundle | `76c21c05fcf3d37cfd09c23a6e7a034eca99c7edadae3457e19a4d10504b3649` |
| Serialized final bundle | `9bb344dc9e908cda1579e2b195da747a1019c18248a42b4add8304cd2a996d3b` |

### Phase 1I

| Anchor | SHA-256 |
| --- | --- |
| Original trade | `9f329e756df247ddc50762b4adfb599648fd05143a6bc3285575863ed05343ea` |
| Corrected trade | `689b1620f3574db605973ba4d8cc940db91fcd5e1f7f5fe488145c80cf5b2fdb` |
| Cancelled trade | `ab16212f35ed7987b9f38e62ca2c3b64a1721c06893c57907c62b5fa37d4eeee` |
| Original quote | `a2572c0458398b81a3c3cf80f22bfc87df78e40e674719f85b946cd7b73c8ede` |
| Corrected quote | `f3898d9ad7698b3defe6ed918581afe22df4423e5f674cc1c9582f246d6909a7` |
| Cancelled quote | `8ab7e85f7e9fe01fa3c2fbf83a880cc00ecbe52b766318da0fdcc34fa2780c54` |
| Mixed JSONL | `856fc303d57e502dee3841b3fe160d6cfd1e0fb1195919f05d119e2d62430a37` |
| Strict replay | `738e66b4573aec86d4ac226247b9b01ee89dc0423fb7935e78ae2e4db22b2f92` |
| Trade/quote series | `68e96fa792d11976c6f1447e1ecf198cb8b05a6c62f01f138b1f0d6a0abc96e8` |
| Final bundle | `f24280a778ca4348ca954c57c174372897ee1a999b3f22a2952d9f7e88dc7295` |
| Serialized final bundle | `a6c29c1dc171db0f5d26c602733ca676f7304d6fe20cf3aecda2ae028f38d8eb` |

Cross-phase embeddings (Phase 1H embeds the four Phase 1G anchors; Phase 1I embeds the four
Phase 1H anchors), standalone fixture hashes, and provider fixture content hashes are also in the
JSON manifest and verified by the same test.

## Why generation is deterministic

The following are the structural reasons repeated generation is byte-identical, all confirmed in
`src`:

- **No wall clock / no randomness.** No `datetime.now`, `time.*`, `random`, `uuid1/uuid4`,
  `os.urandom`, or `secrets` appears in `src` (isolation audit).
- **Deterministic identity.** `observation_id` is a UUIDv5 over a canonical identity dict
  (`deterministic_observation_id`); conflict/revision/relationship IDs are `canonical_hash`
  prefixes over sorted seeds.
- **Canonical serialization.** `canonical_json_bytes` uses `sort_keys=True`, compact separators,
  `ensure_ascii=False`, `allow_nan=False`, UTC timestamp formatting, and normalized `Decimal`
  formatting.
- **Stable ordering.** Replay orders by `observation_order_key`; conflicts, revisions, news
  relationships, diagnostics, observation ages, and coverage all sort by explicit total-order
  keys. Input reordering does not change canonical results where ordering is semantically
  irrelevant (verified by `tests/test_replay_ordering.py` and the lifecycle test).
- **Set/dict determinism.** Iteration over sets/dicts is always wrapped in `sorted(...)` before it
  affects output.
