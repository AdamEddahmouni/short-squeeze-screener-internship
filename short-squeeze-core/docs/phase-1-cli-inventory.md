# Phase 1 CLI Inventory

The `squeeze-core` CLI (`squeeze_core.__main__`) is entirely local and offline. It reads local
files only, opens no network sockets, reads no credentials, writes no database, and emits stable
canonical JSON. Invalid input returns a nonzero exit with a structured JSON diagnostic. No command
emits a rank, score, recommendation, or trading signal. These guarantees are enforced by
`tests/compatibility/test_phase_1_cli_inventory.py` and the per-command suites `tests/test_cli.py`,
`tests/test_market_bar_cli.py`, and `tests/test_trade_quote_cli.py`.

## Commands

| Command | Inputs | Output | Exit codes | Determinism |
| --- | --- | --- | --- | --- |
| `validate` | fixture path | `{command, fixture_hash, observation_count, valid}` on stdout | 0 valid / 1 invalid | canonical JSON, stable |
| `replay` | fixture path, `--mode strict\|normalized` | replay result bytes on stdout | 0 / 1 | stable; strict rejects out-of-order, normalized reorders with a diagnostic |
| `normalize-provider` | `--provider {ibkr,finviz,finra,sec,halts,news,market-bars,trades-quotes}`, `--input`, `--context`, `--case` | normalization result on stdout (accepted) or stderr (rejected) | 0 accepted / 1 rejected | stable canonical JSON |
| `build-evidence` | `--input`, `--symbol`, `--as-of`, `--policy` | point-in-time bundle on stdout | 0 / 1 | stable; `as_of` from `--as-of` is authoritative |
| `build-evidence-timeline` | `--input`, `--symbol`, `--as-of-file`, `--policy` | named bundles on stdout | 0 / 1 | stable; labels processed in sorted order |
| `build-halt-state` | `--input`, `--symbol`, `--as-of` | derived halt state on stdout | 0 / 1 | stable |
| `build-bar-series` | `--input`, `--symbol`, `--interval`, `--as-of`, `--session` | objective bar series on stdout | 0 / 1 | stable |
| `build-trade-quote-series` | `--input`, `--symbol`, `--as-of`, `--provider`, `--venue`, `--market-scope` | objective trade/quote series on stdout | 0 / 1 | stable |

## Cross-cutting guarantees

- **Local files only.** Every input is a `Path`; the only I/O is `read_text`/`read_bytes` on
  local files and `print` to stdout/stderr.
- **Offline.** No HTTP/FTP/WebSocket/DB clients are imported (see the isolation audit).
- **No credentials.** No environment variables, token files, or credential stores are read.
- **Stable ordering.** Output is produced with `canonical_json_bytes` (`sort_keys=True`,
  compact separators, UTC/Decimal normalization). Timeline labels and internal collections use
  explicit sort keys.
- **Nonzero on invalid input.** Any exception is caught and rendered as
  `{command, error, valid:false}` on stderr with exit code 1; provider rejections render a
  structured `{accepted:false, rejection:{code,...}}` on stderr.
- **No strategy output.** `test_phase_1_cli_inventory.py` asserts the output of representative
  commands contains no `squeeze_score`, `ranking`, `recommendation`, `trading_signal`,
  `aggressor`, `sentiment`, indicator, or entry/exit vocabulary (whole-word matched).

## Inventory completeness

`test_all_documented_commands_are_registered` introspects the argument parser and asserts the full
command set above is registered, so a command cannot be documented here without existing in code.
