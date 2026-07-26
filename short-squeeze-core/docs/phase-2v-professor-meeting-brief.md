# Phase 2V — Advisor Meeting Brief

> Outcome-data amendment: the professor's statement is now independently corroborated
> by deterministic historical price evidence at both detection boundaries. It remains
> external corroboration rather than an input to the computation, and the methodology
> is still unverified because the original platform values do not survive.

Short, plain-language summary of what the BIYA case study found. Supporting detail is in
`docs/phase-2v-root-cause-report.md`; the deployable demonstration is in
`apps/biya-validation-demo/`.

## The headline

We reconstructed exactly what the original screener was doing when it surfaced BIYA, and
found the specific defect behind the concerns you raised in the review.

**The "Prime Setup" label was computed from four checks: a price band, a percentage
change, a relative-volume threshold, and a short-float floor. None of those four is a
short-squeeze mechanic.** Borrow fee, days to cover, and the TTM Squeeze indicator were
all being calculated and shown on screen — and none of them fed the label at all.

So the system was doing something reasonable, but not the thing its labels claimed: it
was a momentum-and-liquidity discovery filter presented as a squeeze detector. That one
fact explains both of your observations in the same meeting — LBGJ qualifying at +13%,
and BIYA appearing while its short interest looked low.

## What BIYA's later move does and does not tell us

If BIYA moved sharply afterward, that is genuinely interesting and worth studying. But it
cannot, on its own, tell us the platform's method was sound.

The reason is concrete rather than philosophical. **No record survives of what the
platform actually displayed for BIYA.** The only direct platform record from that session
is an application log, and every reference to BIYA in it is a data-fetch failure — no
price, no short interest, no days to cover, no score, no label. So there is no original
number for a later outcome to confirm or contradict.

A stock rising after it was surfaced tells us about the stock. It tells us nothing about
whether the logic that surfaced it was correct — especially when the same logic would
have surfaced it on momentum alone.

**Formal conclusion: `INSUFFICIENT_EVIDENCE`.** That is a statement about the surviving
record, not a verdict that the platform was wrong.

## What we found in the original platform

Two things worth knowing about the record itself:

- **The code we analyzed is the code that was actually running when you saw BIYA.** The
  classification logic was substantially redesigned about three hours after that meeting.
  Analyzing the current archived version would have described rules that did not yet
  exist.
- **The screener was running on delayed market data.** The account lacked the required
  market-data subscription, so it fell back to delayed prices, with no indicator on
  screen. Cross-provider corroboration failed entirely during the session — the network
  calls did not resolve — and that failure was also invisible in the interface.

Also: the "Short Interest %" column was renamed from "Short Float %" about two hours
before the review. The arithmetic underneath is correct, but it is a *percentage of
float*, while "short interest" usually means an absolute share count. That is consistent
with the value looking lower than expected when you read it.

## Why the rebuild was still necessary

The rebuild is what made the above provable rather than speculative. It gives us
strict point-in-time replay — the ability to ask "what could have been known at that
exact moment?" and get an answer that cannot accidentally include later information.

That capability is what let us establish, rather than assume, that the detection time is
a bounded two-and-a-half-hour window rather than a precise instant, and that no evidence
for BIYA existed in the archive at either edge of it.

## What is worth keeping from the original system

Genuinely good work that should carry forward:

- Per-field quality flags recording exactly which inputs were missing.
- No zero-substitution in the numeric core — missing inputs return "unknown with a
  reason" rather than silently becoming zero.
- Detection of disagreement between a calculated and a provider-supplied value.
- A correctly constructed volume baseline that excludes the incomplete current bar.

**The defects were in labelling and presentation, not in the arithmetic.** That is good
news for Phase 3A.

## What we corrected

- Detection times are now classified as exact, bounded, or unknown, and a filesystem
  timestamp can never be promoted to an exact event time.
- Unknown values stay unknown. They can never become zero, blank, or be back-filled from
  later data.
- Semantically different quantities cannot be compared as if equivalent — a
  percent-of-float and a share count now produce an explicit "different quantity" result.
- The case conclusion is derived from the evidence rather than written by hand, and is
  built so that adding a favourable outcome can never upgrade a case whose original
  values are unrecoverable.

## What the demonstration shows

A single static page: the detection timeline, each original rule with its methodology
classification, the evidence used, the point-in-time replay at both window edges, and an
explicit statement of what could not be established. No scores, no rankings, no
recommendations, no simulated trades.

It is deployment-ready. The Vercel CLI on this machine is not currently logged in, so it
has not been published and no URL is being claimed.

## What Phase 3A will do next

Build a transparent candidate-evaluation framework shaped by these findings: rule-by-rule
PASS / FAIL / UNKNOWN / CONFLICTED / INSUFFICIENT_DATA outcomes, keeping momentum
discovery, short-pressure confirmation, catalyst evidence, and evidence validity
**separate** rather than collapsed into a single label — and with no composite score, no
ranking, and no recommendations.

## Questions for you

1. What exact time did you see BIYA in the platform? Even an approximate answer would
   narrow a two-and-a-half-hour window considerably.
2. Do you have a screenshot or any saved output from that session? A single screenshot
   would recover the original displayed values and change the conclusion materially.
3. Could you forward the message reporting that BIYA squeezed? We could not locate it in
   the project's records, and we do not want to characterize your assessment second-hand.
4. What outcome window counts as a successful prediction — 15 minutes, the session close,
   the next day?
5. Does "short squeeze" require confirmed short-side pressure, or is a large momentum
   move sufficient for the research objective? This changes what the system should be
   built to detect.
6. Which data provider should be authoritative for short interest?
7. Should the research report discovery and confirmation as separate results, rather than
   one combined label?
8. What false-positive rate is acceptable for the research goal?

## One caution

One case cannot validate a methodology. The rule-level findings above apply to every
candidate the platform surfaced, because they come from the code. The BIYA-specific
findings apply only to BIYA — and there, the record is nearly empty.
