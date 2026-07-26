# Deployment

## Docker

```bash
docker build -t short-squeeze-research-screener .
docker run --rm -p 8787:8787 \
  -e SQUEEZE_APP_MODE=FROZEN_DEMO \
  short-squeeze-research-screener
```

Verify `/health`, `/ready`, and `/api/v1/integration/manifest`.

## Railway

Deploy the sanitized source tree, not a private configuration directory or local
ZIP. Set `SQUEEZE_APP_MODE=CLOUD_PROVIDER_MODE` or `FROZEN_DEMO` and provider
values through Railway's secure variable store. Do not configure local IBKR.

The committed `railway.toml` and `Dockerfile` define the build and start boundary.
After deployment, run:

```bash
python tools/integration_acceptance.py --url https://your-service.example --json
```

Review the public responses for secret, account, and local-path leakage before
sharing the URL.
