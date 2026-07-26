# Batch 05 — IBKR Connection and Safety Boundary

## Connection

- **Host:** `127.0.0.1` only. `policy.assert_localhost` refuses anything else.
- **Ports:** probe `4002` then `4001`. The successful port is recorded as *observed
  configuration*, never used to determine account mode.
- **Client ID:** `27185`, fixed fallback `27186 → 27187 → 27188`. Never `0`.
- **Read-only:** the tool assumes the Gateway's Read-Only API is enabled and never alters
  Gateway settings. It cannot place, preview, modify, or cancel orders.

If no local port accepts a connection, verify in IB Gateway:

```
Configure > Settings > API > Settings
[x] Enable ActiveX and Socket Clients
Socket port matches the program (4002 paper / 4001 live)
[x] Read-Only API
```

## Allowed API surface (the only methods the tool references)

```
connect / eConnect, disconnect, isConnected, run, serverVersion,
reqCurrentTime, reqContractDetails, reqHistoricalData, cancelHistoricalData
callbacks: connectAck, nextValidId, managedAccounts (ignored), error,
contractDetails, contractDetailsEnd, historicalData, historicalDataEnd, currentTime
```

## Forbidden API surface (statically guarded — must never appear in tool source)

```
placeOrder cancelOrder reqOpenOrders reqAllOpenOrders reqAutoOpenOrders reqGlobalCancel
reqPositions reqPositionsMulti reqAccountSummary reqAccountUpdates reqAccountUpdatesMulti
reqExecutions reqCompletedOrders reqPnL reqPnLSingle reqMarketDataType reqMktData
reqRealTimeBars reqScannerSubscription reqScannerParameters reqNewsBulletins reqHistogramData
```

`guard.scan_source_for_forbidden` scans every tool `.py` file and fails if any forbidden
method or order/execution object (`Order`, `OrderState`, `OrderCancel`, `Execution`,
`ExecutionFilter`) is referenced. A dedicated test runs this scan on every commit.

## Account-data boundary

- No account, position, balance, margin, execution, P&L, or portfolio API is called.
- The `managedAccounts` callback receives an account list but **never stores or logs it**;
  a test asserts the account identifier is absent from the session state.
- No account identifiers appear anywhere in private or committed outputs (regex-tested).

## Data boundary

- No case association, no outcome computation, no Phase 3A/3B/3C/3E work.
- No live market data, real-time bars, scanner, or news requests.
- No external web retrieval; the only network egress is the local Gateway socket.
