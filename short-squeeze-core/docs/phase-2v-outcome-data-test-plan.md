# Phase 2V Outcome-Data Amendment Test Plan

All amendment tests are offline and use committed sanitized or synthetic fixtures.
Every feature follows red-green-refactor: add one failing behavioral test, run it to
confirm the expected failure, implement the minimum behavior, and rerun the focused
test before the broader suite.

## Manifest and acquisition tests

Cover success, partial, empty, entitlement-required, network-failure, and unsupported
attempts; stable IDs and serialization; exact raw SHA-256; count/range preservation;
explicit retrieval time and request parameters; deterministic ordering; relative paths;
credential-field rejection; and public-output sanitization. Acquisition transport is
tested with saved responses and injected failures, never a live endpoint.

## Market normalization tests

Cover one-minute regular and extended bars, five-minute fallback, daily bars, timezone
conversion, duplicates, conflicts, missing timestamps, missing/zero volume, partial
bars, explicit adjustment status, input-order invariance, stable observation IDs, and
raw acquisition linkage. Existing Phase 1 market-bar normalization remains the canonical
observation path.

## Outcome tests

Cover both BIYA boundaries and every required window: 15 minutes, 30 minutes, one hour,
session close, next-session open, next-session close, 24 hours, and maximum through data
end. Assert the fixed reference policy, positive/negative/flat movement, extrema,
maximum return, adverse movement, time to both extrema, volume, missing reference bars,
incomplete windows, extended-hours separation, partial-bar limitations, and split
adjustment consistency.

Serialized results are scanned to prove the absence of P&L, simulated entry/exit/fill,
position size, recommendation, score, rank, alert, or trade instruction.

## Point-in-time tests

Prove that later market data can describe outcome but cannot enter original replay;
post-boundary news and short-interest publications remain excluded; source/publication
time survives later retrieval; retrieval time never replaces publication time; current
borrow data cannot become historical borrow evidence; short-sale volume cannot become
short interest; and outcome confirmation cannot imply methodology validation.

## Conclusion tests

The additive amendment produces `OUTCOME_CONFIRMED_METHODOLOGY_UNVERIFIED` only for a
substantial fixed-policy market outcome. Missing, flat, contradictory, or adjustment-
incompatible outcome evidence produces `INSUFFICIENT_EVIDENCE`. An article or professor
statement alone cannot confirm market outcome. No amendment path can emit
`VALIDATED_AS_RECORDED`. The original BIYA fixture, case bytes, and Phase 2V anchor remain
unchanged.

## Context-domain tests

News is classified before earliest boundary, within the detection window, after latest
boundary, or unknown. Halt events are attached only when explicitly sourced. Published
short interest and days to cover preserve settlement/publication age and availability at
each boundary. Daily short-sale volume remains a separate collection. Missing historical
borrow stays unavailable. Corporate actions and adjustment policy gate price
comparability.

## Anchors and compatibility

The separate amendment manifest anchors every item required by the handoff, including
success/failure manifests, normalized bars, both references, key windows, contextual
collections, confirmation, updated case, public export, CLI output, and serialized
collection. Generate twice and compare bytes. Run deterministic outcome processing and
public export twice and compare bytes. Verify all Phase 1, 2A, 2B, 2C, 2D, and original
2V anchor files against starting HEAD `232cc7e`.

## Demo and security tests

Build the static demo, serve locally, and verify desktop and mobile layouts. Confirm the
outcome section shows both boundaries, fixed reference policy, required windows,
extrema, timing, context, limitations, and exact methodology conclusion. Scan generated
outputs for credentials, tokens, authentication parameters, cookies, account IDs,
emails, phone numbers, absolute paths, and private URLs. Source forensic artifacts are
never rewritten by this scan.

## Final commands

Run the full suite and dedicated validation, readiness, metrics, and compatibility
suites with the exact fresh `--basetemp` paths from the amendment handoff. Verify the
demo build, Vercel authentication state, Git cleanliness, no remotes, no push/merge,
unchanged prior anchors, and all three archive checkpoints.

