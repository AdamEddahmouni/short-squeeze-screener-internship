# Integration Team Handoff

Branch: `batch/independent-prime-dashboard-railway-14`

Implementation checkpoint: `f8ae0010bc2ed9ce982c4a1f53a24cdc92d737fb`

Repository layout:

- `apps/research_screener/methodologies/`: backend methodology policies and projection;
- `apps/research_screener/static/`: dependency-free dashboard and SVG landscape;
- `apps/research_screener/demo_data/`: sanitized frozen aggregate and manifest fixture;
- `apps/research_screener/{server,deployment,api_contract}.py`: modes and API boundary;
- `Dockerfile`, `railway.toml`, `.dockerignore`: Railway packaging;
- `tests/app/test_batch14_*.py`: offline deterministic Batch 14 coverage.

Launch locally:

```powershell
.\run_screener.ps1
```

Launch cloud mode locally:

```powershell
$env:PORT=8787
.\.venv\Scripts\python.exe -m apps.research_screener --mode CLOUD_PROVIDER_MODE --no-browser
```

Modes are `LOCAL_FULL`, `CLOUD_PROVIDER_MODE`, and `FROZEN_DEMO`. Local mode binds
`127.0.0.1`; cloud binds `0.0.0.0:$PORT`; frozen demo is network-free. Health is
`/health`, readiness is `/ready`, and the full route/schema contract is in
`docs/integration-api-contract.md`.

Environment variable names only: `SQUEEZE_APP_MODE`, `PORT`, `FINVIZ_API_KEY`,
`NEWSAPI_KEY`, `FINNHUB_KEY`. Railway status is `DEPLOYMENT_READY_AUTH_REQUIRED`; see
`docs/batch-14-railway-deployment.md`.

The candidate store remains authoritative. Methodologies are immutable projections.
Filters/sorts operate on view copies. Fake-provider tests inject `SyntheticProvider`;
normal tests never read private configuration or call external services. Frozen demo
reproduces 97 PASS / 20 FAIL / 208 UNKNOWN across 13 candidates and is explicitly not
the private canonical tree.

Canonical Phase 3A, research detection, the Phase 3B registry, archived repositories,
and frozen research are integration boundaries. Current enrichment never fills frozen
gaps. Trading, orders, and account access are unsupported.

Known limitations: peer formulas are incomplete; Adam predictive performance is
unvalidated; current evidence may make every candidate unevaluable; local IBKR cannot
operate on Railway; TTM and sentiment are not implemented; Railway awaits login.
