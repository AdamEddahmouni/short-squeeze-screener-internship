# Batch 04 — Security, Entitlement, and Credential Boundary

## No network, no accounts, no automation of acquisition

This batch adds no capability to reach the network. It does not download data, call
provider APIs, scrape sites, create or log into accounts, or automate downloads. It
does not bypass authentication, rate limits, robots rules, anti-bot measures, or
paywalls, and it does not execute any archived authentication or impersonation
helper. The operator obtains any real export themselves, lawfully, outside this
software.

The acquisition isolation guard (`tests/acquisition/test_isolation.py`) statically
forbids network, database, environment, ML, and dataframe imports and any
wall-clock or random call anywhere under `src/squeeze_core/acquisition/`, including
this package.

## Credentials are never handled

No credential material (a login pass-phrase, API key, or token) is requested, read,
logged, printed, or stored by this batch. `schwab_tokens.json` and any other
credential file are never touched. Templates and manifests carry provenance and
semantics only; the credential-scan tests assert that no credential-like token
appears in any committed kit or fixture file. Credentials are never redacted,
rewritten, rotated, or cleaned as a side task.

## Entitlement is an assertion, not a determination

The manifest records the operator's `user_entitlement_assertion` and an optional
`license_or_terms_reference`. The software stores these as declarations. It makes
**no** legal determination that the operator is entitled to use an export, and a
recorded assertion is not a substitute for actually holding the rights. Operator
documentation instructs the user to supply only exports they are entitled to use,
and never advises bypassing a source restriction.

## Raw bytes and private data

The raw artifact bytes are never modified by any part of the workflow; regenerated
canonical outputs are written separately. The private intake root
`intake/local-bars/` remains git-ignored so a real licensed export is never
committed. No real licensed market-data export is committed in this batch; every
committed example is synthetic and unmistakably fictional. Absolute, machine-specific
paths never enter any deterministic identity.
