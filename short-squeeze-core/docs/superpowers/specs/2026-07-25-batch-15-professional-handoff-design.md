# Batch 15 Professional Handoff Design

## Objective

Turn the Batch 14 research screener into a provider-swappable, privacy-safe,
professionally documented handoff without changing frozen research results,
canonical registries, archived repositories, or the local private provider file.

## Scope and priorities

Batch 15 prioritizes a clean integration release over optional product additions.
Phase 3E, predictive validation, backtesting, P&L analysis, threshold optimization,
trading, order access, and account access remain out of scope.

## Architecture

### Configuration

`apps.research_screener.config` owns application, runtime, provider, refresh, and
deployment settings. Resolution is deterministic: command arguments, process
environment, explicit configuration file, the local private file in `LOCAL_FULL`,
then safe defaults. Tests, cloud mode, frozen mode, and fake-provider mode never
load the local private file implicitly.

Provider enable flags are distinct from credential presence. Disabled providers
report `DISABLED`; enabled but unconfigured providers report `NOT_CONFIGURED`.
The configuration doctor emits human-readable or JSON status and never returns
credential values.

### Release boundary

`tools/build_handoff_release.py` constructs a new staging directory from a
committed allowlist. It never copies the repository root wholesale. A release
audit rejects forbidden filenames, credentials, personal/academic markers,
absolute user paths, private data, caches, and generated build residue.

The release contains runtime source, safe demo data, safe tests, launch and
deployment files, professional documentation, an integration manifest, release
metadata, dependency inventory, and checksums. It excludes Git metadata, private
configuration, raw evidence, provider caches, local test output, and internal
historical/academic documents.

### Integration verification

`tools/integration_acceptance.py` checks the stable API, integration schema,
providers, frozen totals, methodology endpoints, export behavior, and the absence
of trading/account endpoints. It supports a running URL and frozen in-process
checks. `morning_check.ps1` composes repository, configuration, release, checksum,
and acceptance checks without printing secrets.

### Product changes

Canonical research semantics remain unchanged unless an existing canonical rule
has a demonstrably compatible evidence mapping. Finviz Float and timestamped news
are traced through current evidence adapters with focused regression tests.
Provider Relative Volume remains display-only unless its raw inputs meet the
canonical definition. Optional indicators or sentiment are additive,
experimental, disabled by default, and never alter Evidence-Gated Prime.

## Security and privacy

The current `.private/providers.env` is read-only for this batch. No scanner,
doctor, test, release builder, log, error, manifest, or documentation output may
print its values or its absolute path. A private ignored pattern file may extend
the generic release scanner without committing personal terms.

Public errors use stable codes and sanitized messages. Public documentation uses
organization-neutral terminology. Backward-compatible machine methodology IDs
remain stable; display labels become neutral.

## Testing

New behavior follows red-green-refactor cycles. Offline tests cover precedence,
mode isolation, provider disabling, doctor redaction, release allowlisting,
forbidden-file and content detection, manifest/checksum generation, extracted ZIP
smoke behavior, acceptance checks, evidence mappings, and API compatibility.

The final gate is a fresh full pytest run with JUnit output, followed by Git diff,
secret/privacy/path scans, release extraction, frozen-mode startup, HTTP smoke
checks, and checksum verification.

## Deliverables

The working tree receives the configuration layer, tools, professional documents,
safe environment template, release metadata, and tests. Generated release
artifacts live under ignored `dist/` and are not committed unless repository
policy changes. A completion report and next-batch handoff record exact verified
results and explicitly state that Phase 3E was not started.
