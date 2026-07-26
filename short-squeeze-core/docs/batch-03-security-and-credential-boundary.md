# Batch 03 — Security and Credential Boundary

This project is local-only. Batch 03 adds no exception to that.

## The workflow never

- asks for credentials, or reads any existing credential or token file
  (`schwab_tokens.json` is never touched);
- accesses a provider account, brokerage, or market-data service;
- calls a provider API, scrapes any site, or performs any **network** access;
- bypasses authentication, rate limits, robots rules, or anti-bot controls;
- executes any archived authentication or TLS-impersonation helper;
- prints, redacts, rotates, or rewrites credential values.

The acquisition isolation guard (`tests/acquisition/test_isolation.py`) statically
proves the new package imports no network/database/ML/dataframe library and makes
no environment, random, or wall-clock calls.

## What the workflow does accept

Files the user has **independently** exported and placed locally, under a private
intake root. That root (`intake/local-bars/`) is gitignored, so real user-supplied
licensed market data is never committed. Real data would be committed only if the
user later gives explicit authorization for the exact files.

## Credential-like values

`CREDENTIAL_LIKE_TOKENS` enumerates secret-like substrings (password, secret,
api_key, access_key, private_key, client_secret, auth/access/refresh tokens,
`bearer `, authorization). A committed-fixture guard
(`test_batch03.py::test_no_credential_like_values_in_any_fixture`) asserts none of
these appear in any batch-03 fixture. All fixtures use unmistakably synthetic
dummy provider names (`DEMO_HISTDATA_EXPORT`) and dummy symbols (`ZZAA`).

## Entitlement is provenance, not a legal ruling

`user_entitlement_assertion` records the user's own statement of entitlement for
provenance. The software makes no legal or source-entitlement determination; it
validates integrity and semantics only.
