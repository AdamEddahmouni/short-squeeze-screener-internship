# Provider and Entitlement Guide

Obtaining the file and using the software are separate steps.

## Obtaining a file lawfully

You obtain the export yourself, through means you are permitted to use: your own
licensed download, a permitted export from a tool you have rights to, or another
lawful source. The kit does not download data, call APIs, scrape sites, log into
accounts, or bypass paywalls, rate limits, robots rules, or anti-bot measures.
Supply only exports you are entitled to use under their terms.

## Declaring what you obtained

In the manifest you declare provenance and your entitlement assertion:

- `provider_name` — the data source or provider.
- `provider_product_or_export_name` — the specific product or export.
- `user_entitlement_assertion` — your statement that you are entitled to use it.
- `license_or_terms_reference` — a reference to the terms, or null.
- `retrieval_time` — when you retrieved it (UTC).
- `export_time` — when the provider produced it (UTC).

The software records your entitlement assertion. It makes **no** legal
determination. Recording an assertion is not a substitute for actually holding
the rights.

## Never include credentials

Do not paste any credential material (a login pass-phrase, API key, or token)
into a manifest, a mapping profile, a file name, or the raw data. Declarations
carry provenance and semantics only.
