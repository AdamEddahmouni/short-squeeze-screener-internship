# Batch 13 Test and Verification Report

Focused application, provider, compatibility, acquisition, isolation, and truthfulness
guard runs passed before the authoritative run.

- JUnit: `C:\Users\adame\.codex\visualizations\2026\07\25\019f9ad6-239f-7231-bc67-dbb2cd903342\batch13-final-v3\batch13-final.xml`
- Tests: 2,537
- Passed: 2,536
- Skipped: 1
- Failures: 0
- Errors: 0
- Process exit code: 0
- Duration: 111.330 seconds
- External network attempts during ordinary tests: zero, enforced by the autouse guard
- Private config loading during tests: disabled by construction

Manual verification:

- Dashboard and health routes: HTTP 200
- Current discovery smoke: 15 candidates
- Current evaluable rules: 9 / 25; newly evaluable rules: none
- NewsAPI: 10 AAPL headlines
- Finnhub: price returned
- SEC EDGAR: 30 AAPL filings
- IB Gateway: localhost port 4001 reachable
- Finviz: configured; official export returned HTTP 401 invalid token
- Current JSON/CSV export: scanned against every configured credential value; no leak

The sandboxed background app cannot make outbound calls, but it serves the dashboard.
The direct read-only provider smoke completed except for the Finviz credential response.
