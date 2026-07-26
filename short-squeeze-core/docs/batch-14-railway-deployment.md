# Batch 14 Railway Deployment

Decision: **DEPLOYMENT_READY_AUTH_REQUIRED**.

Prepared and tested:

- root `Dockerfile` using Python 3.12 and a non-root `app` user;
- writable `/app/exports`;
- `.dockerignore` excluding `.private`, raw local bars, caches, JUnit output, Git data,
  tests, and local environments;
- `railway.toml` using the Dockerfile, `/health`, 300-second health timeout, and
  `ON_FAILURE`;
- `CLOUD_PROVIDER_MODE` binds `0.0.0.0:$PORT`;
- cloud-safe providers read only `FINVIZ_API_KEY`, `NEWSAPI_KEY`, and `FINNHUB_KEY`;
- local IBKR is unavailable and is not loopback-probed in cloud;
- frozen demo, readiness, comparison, export, and secret-response smoke checks pass.

The official Railway CLI was run transiently at version 5.28.1. Both `whoami` and
`status` returned `Unauthorized`. The deployment was therefore not uploaded and no
project was created or selected.

Exact remaining user action:

```powershell
npm.cmd exec --yes @railway/cli -- login
```

After authentication, rerun this Batch 14 task so Codex can select/create the intended
project, run `railway up`, generate/verify the domain, and perform the public smoke.

The local Docker CLI exists, but Docker Desktop's Linux daemon was not running. The same
production entrypoint passed a direct cloud-mode server and headless-browser smoke.
