# Batch 14 — Authorized Finviz Elite Refresh Plan

## Authorization and purpose

The user states that the Finviz Elite account is their legitimate account and authorizes
the instructor-directed, project-supplied authentication flow for read-only retrieval of
supported Finviz Elite screener/export data. This batch does not bypass payment,
ownership, MFA, CAPTCHA, or provider limits.

## Reviewed source and active boundary

- Read-only source reviewed:
  `archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/core/finviz_auth.py`
- Supported targets: Finviz login submission, the authenticated Elite API explanation
  page, and the official Elite screener export endpoint.
- The archive remains immutable. Only the minimal login/token-discovery behavior may be
  reimplemented under active operational tooling.
- The tool is manual, local-only, excluded from canonical research packages, inert on
  import, and never invoked by normal tests or application startup.

## Security and stop conditions

- Credentials come only from the Git-ignored private provider file or secure local input.
- No token, password, cookie, authorization header, or authenticated URL is printed or
  written to a tracked path.
- The private file is backed up within `.private/`, updated atomically, and validated
  before replacement.
- Tests use synthetic transports and retain the suite-wide network guard.
- Stop immediately for MFA, CAPTCHA, ambiguous/login-page responses, account lockout,
  unsupported provider behavior, or any request outside the user-owned read-only flow.
- Phase 3E, trading, account data, and order functionality remain out of scope.
