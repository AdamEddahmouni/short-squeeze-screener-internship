# Batch 14 Finviz Token Refresh and Validation

Status: authorized refresh completed successfully on 2026-07-25.

- Scope: the user's legitimate Finviz Elite account and official Elite export route only.
- Access: the archived login flow was audited read-only; only required curl-cffi browser
  profile and token discovery behavior were ported.
- Safety: explicit invocation, sanitized output, atomic private-file replacement, private
  backup, restrictive file handling, and no import-time execution.
- Command: `.\refresh_finviz_token.ps1`
- Authentication: session accepted; current `userToken` field discovered.
- Validation: official CSV export returned HTTP 200 and 1,469 data rows.
- Backup: `.private/backups/providers.env.pre-finviz-20260725T203848Z.bak`
- Git: the provider file and backup are ignored.

Columns: `Ticker`, `Shares Float`, `Insider Ownership`, `Short Float`, `Short Ratio`,
`Short Interest`, `Performance (Week)`, `Performance (Month)`, `Average True Range`,
`Volatility (Week)`, `20-Day Simple Moving Average`, `50-Day Simple Moving Average`,
`50-Day High`, `Relative Strength Index (14)`, `50-Day Low`, `Change from Open`, `Gap`,
`Relative Volume`, `Price`, `Change`, `52-Week High`, `Prev Close`, `Open`, `High`.

Timing: fetch 0.2815 s; parse 0.0079 s; total 0.2906 s; cache TTL 120 s.
No token, password, cookie, or session value is recorded here.
