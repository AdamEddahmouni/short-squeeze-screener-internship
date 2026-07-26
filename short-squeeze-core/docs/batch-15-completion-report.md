# Batch 15 Completion Report

## Decision

The professional distributable is verified for local delivery. Full repository
handoff is not complete: a redacted exact tracked-HEAD audit still identifies
legacy internal research records, class-era terminology, historical local paths,
and intentional synthetic scanner/compatibility patterns that are excluded from
the release. Railway deployment is also blocked because the CLI reports that
authentication is required.

## Product and configuration

- Central configuration precedence is command line, process environment, explicit
  configuration file, explicit local private file in `LOCAL_FULL`, then safe default.
- Finviz, NewsAPI, Finnhub, SEC EDGAR, and IBKR can be disabled independently.
- Disabled providers report `DISABLED`.
- The configuration doctor supports text and JSON output without values or paths.
- The existing local private provider file was not modified.
- Local doctor status: Finviz, NewsAPI, Finnhub, and SEC configured; IBKR local
  configuration present and socket reachable.
- Public display terminology is organization-neutral. Stable machine identifiers
  and one legacy API alias remain for compatibility.

## Product evidence

The existing Finviz Float pipeline was verified end to end. A controlled current
candidate moves from 11/25 to 12/25 supported canonical rules when valid Float
evidence is supplied; `FLOAT_MAXIMUM` becomes the exact newly evaluable rule.

Timestamped news remains display evidence and does not automatically produce a
positive catalyst result. Provider Relative Volume remains display-only because
canonical session and baseline compatibility has not been established. Published
Short Interest, Days to Cover, shortability, Shortable Shares, and Borrow Fee remain
unknown when semantically matching evidence is absent. TTM Squeeze and FinBERT
sentiment were deferred behind the mandatory handoff work.

## Release and privacy

- Release version: `0.15.0`
- Release builder: `python tools/build_handoff_release.py --version 0.15.0 --json`
- Staged file count: 376
- Release audit: PASS with zero unreviewed findings
- Reviewed compatibility matches: 8
- Personal information in release: 0
- Class or correspondence documents in release: 0
- Credential values in release: 0
- Private provider files in release: 0
- Unreviewed local absolute paths in release: 0
- Internal checksums: PASS
- Clean extraction import: PASS
- Release smoke tests: 3 passed
- Frozen HTTP integration acceptance: PASS
- Fresh environment dependency install: PASS

The generated `RELEASE_MANIFEST.json`, `CHECKSUMS.sha256`, ZIP, and ZIP checksum
sidecar under `dist/` are authoritative for the final build.

## Tracked source-tree audit

The exact tracked-HEAD export contains 1,402 scanned files and does not yet meet
the zero-finding active-tree sanitization criterion. Redacted findings were:

- academic or personal category: 73 matches across 34 files;
- authenticated URL pattern: 1 match across 1 file;
- credential-shaped synthetic pattern: 2 matches across 2 files;
- email pattern: 3 matches across 2 files;
- phone pattern: 1 match across 1 file;
- Unix user-home path: 8 matches across 6 files;
- Windows user-home path: 14 matches across 11 files.

The findings include historical internal documentation and deliberate negative
test inputs. No matched value is reproduced here. These tracked-source findings
do not enter the allowlisted release, whose audit passes with zero unreviewed
findings.

## Verification

Authoritative suite:

- tests: 2,623
- passed: 2,622
- skipped: 1
- failures: 0
- errors: 0
- duration: 177.120 seconds

Integrity:

- Frozen totals: 97 PASS / 20 FAIL / 208 UNKNOWN
- Batch 05 private artifacts: 26 artifacts / 0 mismatches
- Batch 08 Phase 3A artifacts: 26 artifacts / 0 mismatches
- Archived parent: `0897562e05d75b812dd284de81dfafdfa1dea916`
- Archived nested application: `6dbefd1a6b271bfc48106c4aa002f211735551cd`
- Canonical registries: unchanged
- Forward outcomes: not accessed
- Trading, order, position, and account capabilities: absent

No predictive validation, backtesting, P&L analysis, or threshold optimization was
performed. Phase 3E was not started.
