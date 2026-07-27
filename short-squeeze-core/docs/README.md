# Documentation index

Version **0.16.0**. This index is the map of **current-truth** product documentation.
Historical batch and phase reports remain in this tree for provenance; they are not
the operational guide.

This product is a **read-only research screener**. It does not place orders, access
brokerage accounts, recommend trades, or claim predictive validation.

## Start here

| Audience | Document |
|---|---|
| New engineer or integrator | [Getting Started](getting-started.md) |
| Package overview | [../README.md](../README.md) |
| Integration handoff | [../HANDOFF_README.md](../HANDOFF_README.md) |
| What the product does not do | [LIMITATIONS.md](LIMITATIONS.md) |

## Tutorials (learning-oriented)

| Document | Outcome |
|---|---|
| [Getting Started](getting-started.md) | Clone → Python 3.12 venv → install → configure → run frozen demo → verify `/health` |

## How-to guides (task-oriented)

| Document | Task |
|---|---|
| [How-to guides](how-to-guides.md) | Cloud/Railway, providers, frozen demo, collectors, deploy-sync, morning checks, security locks |
| [Collectors](COLLECTORS.md) | Enable and operate supplemental evidence collectors |
| [Deployment](DEPLOYMENT.md) | Docker and Railway deploy boundary |
| [Railway IB Gateway](railway-ib-gateway.md) | Optional IBKR sidecar on Railway (private network) |
| [Integration](INTEGRATION.md) | Swap providers and run acceptance checks |

## Reference (information-oriented)

| Document | Contents |
|---|---|
| [CONFIGURATION.md](CONFIGURATION.md) | Precedence, environment variables, doctor |
| [API.md](API.md) | HTTP routes and integration contract |
| [openapi.json](openapi.json) | Static OpenAPI 3 description |
| [PROVIDERS.md](PROVIDERS.md) | Provider capabilities and admissibility |
| [METHODOLOGIES.md](METHODOLOGIES.md) | Scoring dimensions, thresholds, labels |
| [TESTING.md](TESTING.md) | Offline test commands |
| [SECURITY.md](SECURITY.md) | Credential boundary and opt-in API locks |
| [CLI and Make](CLI.md) | Entrypoints and Makefile targets |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [../.env.example](../.env.example) | Environment template (placeholders only) |

## Explanation (understanding-oriented)

| Document | Topic |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Surfaces, runtime, evidence pipeline, release boundary |
| [Reproducibility](reproducibility.md) | Frozen/offline vs live credentials; research vs live app |
| [LIMITATIONS.md](LIMITATIONS.md) | Explicit non-goals and incomplete validation |

## Ports and modes (quick facts)

| Fact | Value |
|---|---|
| Default local port | `8787` (`PORT`, binds `127.0.0.1` in local/frozen) |
| Docker Compose host URL | `http://127.0.0.1:8787/` (maps host `8787` → container `8080`) |
| Container / Railway listen | `0.0.0.0:$PORT` (Compose sets `PORT=8080` inside the container) |
| Modes | `LOCAL_FULL`, `CLOUD_PROVIDER_MODE`, `FROZEN_DEMO` |

## Historical archive (not current truth)

Leave the following in place for audit history. Prefer the documents above for
day-to-day work. Do not treat batch/phase reports as the live product contract.

| Pattern | Role |
|---|---|
| `batch-*.md` | Historical batch completion, handoff, and verification notes |
| `phase-*.md` | Phase design, progress, and acquisition reports (including Phase 3E stage work) |
| `adr/` | Architecture decision records |
| `superpowers/` | Internal plans and specs |
| Meeting / academic note filenames | Non-product context (excluded from public handoff checks) |
| `release/` | Privacy and handoff audit notes |
| `testing-and-validation.md` | Older validation narrative; prefer [TESTING.md](TESTING.md) |

When a historical report conflicts with a current-truth document (for example an
older “Phase 3E has not started” note versus a later stage-2 completion report),
**trust the current-truth set and [CHANGELOG.md](CHANGELOG.md)**, then read the
historical file only for provenance.
