# Integration

## Stable contracts

- API version: `1.0.0`
- Integration schema: `batch14.integration.v1`
- Health path: `/health`
- Readiness path: `/ready`
- Manifest path: `/api/v1/integration/manifest`

New response fields are additive. Integrations must tolerate explicit nulls and
unknown enum values. A missing value is never equivalent to zero.

## Acceptance

```bash
python tools/integration_acceptance.py --mode frozen
python tools/integration_acceptance.py --url http://127.0.0.1:8787 --json
```

Acceptance verifies versions, frozen totals, providers, methodologies, manifest,
exports, and the absence of trading/account endpoints.

## Provider swap

Change the provider environment value, restart, run the doctor, then verify
`/api/providers`. No source edit is required. Disable unused providers explicitly.

## Security boundary

Integrators receive source and safe demonstration data, not existing provider
credentials, private raw evidence, account data, or Git history.
