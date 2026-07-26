# Timezone, Interval, and Session Guide

## Timezone

- The manifest's `event_timezone` describes the bars' event time, which is kept
  separate from `retrieval_time` and `export_time`.
- Prefer `UTC` or an explicit offset like `-05:00`. A named IANA zone (for example
  `America/New_York`) is supported only when IANA time-zone data is available in
  your environment; otherwise it resolves as an unknown timezone and blocks
  normalization. Use UTC or an explicit offset when in doubt.
- An unknown timezone blocks normalization; it is never guessed.
- A local timestamp that is ambiguous (a daylight-saving fall-back) or nonexistent
  (a spring-forward gap) blocks that row; it is never resolved by guessing. Provide
  UTC or an explicit offset to avoid the ambiguity.
- The timezone cannot be inferred from the symbol or venue alone.

## Interval

- Supported fixed intervals: 1_MINUTE, 5_MINUTES, 15_MINUTES, 30_MINUTES, 1_HOUR, 1_DAY.
- Session-based intervals (for example `1_DAY`) are not bounded this batch and
  block the bundle as an unsupported interval. Daily or irregular bars are never
  silently converted to a supported interval.
- Declare a single interval per bundle. Rows that imply mixed intervals are not
  silently reconciled.
- `timestamp_semantics` (`START` or `END`) determines whether a row timestamp marks
  the bar's start or end; the other boundary is derived from the interval.

## Session coverage

- Declare `session_coverage` as one of: PREMARKET, REGULAR, AFTER_HOURS, OVERNIGHT, EXTENDED, CLOSED_SESSION, UNKNOWN.
- `session_coverage_policy` is one of: ALLOW_GAPS, REQUIRE_CONTINUOUS.
  `REQUIRE_CONTINUOUS` reports a coverage gap between non-adjacent bars;
  `ALLOW_GAPS` permits gaps (for example around halts or closed sessions).
- Declared coverage is what you assert; observed coverage is what the bars show.
  Coverage cannot always be inferred from timestamps alone, so you declare it.
