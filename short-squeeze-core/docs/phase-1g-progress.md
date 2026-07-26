# Phase 1G Progress

Phase 1G is implemented on `phase/1g-offline-news-evidence` as local-only deterministic objective news evidence.

## Delivered

- frozen strict provider-neutral record plus documented Finviz-, Yahoo-, and NewsAPI-shaped aliases
- unchanged schema `1.0.0` and unchanged canonical `NewsItemPayload`
- deterministic URL, timestamp, explicit-symbol, duplicate, conflict, lifecycle, and syndication semantics
- independent `NEWS` coverage and distinct publication, update, availability, capture, receipt, and effective ages
- 35 representative/synthetic provider cases, a 15-observation mixed replay, and six point-in-time timeline bundles
- local CLI normalization and reuse of the existing replay/evidence/timeline frameworks
- ADRs 0020–0022 for availability, explicit symbol association, and immutable news lifecycle handling

## Deterministic anchors

- mixed JSONL: `7eab70a7aac2526c2b76d8af4d7c6c246fb6738beabfc71b8075580e0a4e4001`
- strict replay: `8ac4ffb2e15ee2a4f19e6e6eb8320527cdbbd24f36d99261c007b14394d74aee`
- final bundle: `90ab29e174a258d5c873a0c12bf425297cb7ee8636ec369730837ab4a3153763`
- serialized final bundle: `b328c8789073f3bccc9dcb15e31fe776e40e7daf955ac87179f4b43e8859e2ec`

All Phase 1A–1F compatibility anchors remain unchanged. The suite contains 394 tests.

## Explicit exclusions

There is no live news client, feed or article fetch, sentiment, catalyst direction, materiality or relevance score, semantic deduplication, entity or symbol inference, generated summary, ranking, recommendation, trading interpretation, persistence service, web API, GUI, or order path. Phase 1H has not begun.
