# Phase 1I Progress

Phase 1I is implemented on `phase/1i-offline-trades-quotes` as local-only deterministic trade and quote evidence.

## Delivered

- strict provider-neutral trade/quote model with exact prices, nullable whole sizes, objective conditions, venue, market scope, sequence scope, and four operational times
- schema `1.0.0` with a backward-compatible nullable trade size and objective crossed-quote validation
- immutable original, corrected, cancelled, deleted, duplicate, conflict, and cross-provider records
- independent `TRADES` and `QUOTES` coverage, five separate ages, revision relationships, and compatible conflicts
- deterministic sequence-aware series with arrival/event/sequence separation and normal/locked/crossed/one-sided structural states
- representative/synthetic fixtures, mixed replay, local CLI, deterministic hashes, and unchanged Phase 1A-1H anchors

## Explicit exclusions

There is no live access, download, stream, depth book, synthetic NBBO, trade aggregation, aggressor side, buy/sell volume, order-flow or imbalance metric, midpoint or spread, slippage, liquidity/execution score, momentum, squeeze probability, rank, recommendation, entry, exit, order, or signal.

