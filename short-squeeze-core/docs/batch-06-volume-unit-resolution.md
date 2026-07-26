# Batch 06 — Historical Volume-Unit Resolution (Shares vs Round Lots)

## Distinction

The volume **unit** (shares vs round lots) is a scaling concern, entirely distinct from
**corporate-action adjustment** of volume. The `IntakeManifest` (schema 1.0.0) has **no
volume-unit field**, so the unit never gates preflight — it is recorded as provenance only.

## Official context (not a per-collection fact)

`market_data.html` (OD, accessed 2026-07-25) states US-stock size quotes were previously
in round lots (of 100 shares) and, effective TWS 985+, are displayed in shares with a
compatibility option. This concerns market-data **size quotes**; official docs do not tie
the **historical bar volume unit** of a specific collection to a single setting name in a
way recoverable here. The relevant fact is the Gateway setting in effect **during Batch 05
collection**, which must be established from evidence, not assumed.

## Evidence hierarchy applied

**Level 1 — existing Batch 05 capture: NOT CAPTURED.**
The Batch 05 request manifest records `what_to_show=TRADES`, `use_rth=0`, `format_date=2`,
`bar_size_setting="1 min"`, `duration_str="86400 S"`, and the connection probe records
host/port/client_id/server_version=223 — but **no** volume-lots setting. The setting was
not captured.

**Level 2 — read-only local IB Gateway configuration: NOT ESTABLISHABLE SAFELY.**
Read-only inspection of `C:\Jts\ibgateway\1045`:
- `jts.ini` is plaintext but contains only connection/UI keys (no lots/shares/market-data
  key).
- The API settings live in per-day `ibg.*.xml` files, which are **obfuscated binary**
  (`file` reports `data`; no plaintext `lot`/`shares` tokens present).
Establishing the setting would require decoding an obfuscated file — i.e. guessing /
reverse-engineering — which is not a safe, unambiguous establishment. No account IDs or
credentials were read; only setting-key presence was probed.

**Level 3 — live Gateway UI: DECLINED.**
Reading the checkbox in the running Gateway (Configure → API → Settings) is invasive on the
live authenticated session and does **not** change any preflight verdict (no manifest
field). Declined by policy; the current UI state also would not prove the state in effect
during Batch 05 collection.

**Level 4 — outcome: `HISTORICAL_VOLUME_UNIT_UNRESOLVED`.**
The unit cannot be established without guessing. It is **never** inferred from bar
magnitudes, OHLCV patterns, or the Gateway build number. Recorded honestly as unresolved.

## Recorded result

```
HISTORICAL_US_STOCK_VOLUME_SETTING = HISTORICAL_VOLUME_UNIT_UNRESOLVED
evidence_source_path_category    = C:/Jts/ibgateway/1045 (jts.ini plaintext; ibg.*.xml obfuscated binary)
configuration_key_name           = (none recoverable)
read_only_observation_time       = 2026-07-25 (fixed access date; no account data read)
```

This is an accepted honest completion state (handoff §27: "resolved or honestly remains
unresolved"). Because the unit is not a manifest field, it has no effect on the
re-preflight verdict.
