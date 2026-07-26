# Batch 13 Finviz Integration

The adapter uses the legitimate Finviz Elite CSV export endpoint
`https://elite.finviz.com/export/screener` with an account export token. The archived
login/TLS helper was inspected only as historical evidence and was not executed,
imported, or copied.

The global export refreshes into an in-memory cache. Normalized display fields include
ticker, company, sector, industry, country, price, change, volume, average volume,
relative volume, market cap, shares outstanding, float, short float, short ratio, and
earnings date. Displayed cells retain provider, time, status, value, missing reason, and
readiness.

Sanitized status:

- Configuration: `CONFIGURED`
- Authentication: `INVALID_CREDENTIAL`
- Result: HTTP 401, invalid export API token
- Rows returned: 0
- Cache: adapter retains any last-good snapshot on later failures

No fallback scraping or interactive login automation is used.
