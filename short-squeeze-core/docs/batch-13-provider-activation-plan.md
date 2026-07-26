# Batch 13 Provider Activation Plan

Production provider activation is explicit and runtime-scoped.
`run_screener.ps1` passes `.private/providers.env` to the entry point. Imports,
ordinary CLI use, and tests start with an offline `ProviderBundle`.

1. The launcher opts into the private configuration path.
2. The entry point constructs real Finviz, NewsAPI, Finnhub, and SEC clients.
3. `ScreenerSession` receives that bundle.
4. Explicit refresh calls populate provider caches.
5. Rendering reads caches only and performs no external request.
6. Tests inject offline or fake bundles. A suite-wide guard records any external
   DNS/socket attempt while permitting loopback server tests.

Finviz uses only the supported Elite CSV export route. NewsAPI uses its official
`v2/everything` route. Secrets are passed as request parameters and redacted from
operational errors.
