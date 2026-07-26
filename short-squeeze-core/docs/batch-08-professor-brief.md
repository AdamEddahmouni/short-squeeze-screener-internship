# Batch 08 — Professor Brief

Short-squeeze research reconstruction. Status as of the Batch 08 checkpoint.

One-line summary: the system can now take 13 real, outcome-blind historical candidates and
run a transparent 25-rule evaluation against verified point-in-time evidence — and it is
explicit about which rules it can honestly answer (3 of 25) and which it cannot (22).

---

## What is now working

**Canonical point-in-time evidence architecture.** One engine decides what was knowable at
a given instant, across every evidence domain. Nothing downstream re-implements that rule;
a test fails the build if a second point-in-time filter starts to grow.

**Deterministic metrics and readiness.** Metrics and readiness records are content-addressed
(UUIDv5 over canonical JSON). Re-running produces byte-identical output. Verified twice
this batch: the full private generation was run twice and diffed byte-for-byte.

**Transparent 25-rule Phase 3A evaluation.** Every rule carries an explicit threshold, a
provenance record for where that threshold came from, and a closed outcome vocabulary that
includes `UNKNOWN` and `INSUFFICIENT_DATA` — so missing evidence is never silently
converted into a negative answer.

**Controlled historical acquisition.** Candidates were curated from an archived scanner
snapshot with a frozen detection boundary, before any market data was touched.

**13 real frozen cases.** XNCR, PESI, SLS, ZNTL, GPRE, SSPC, LBGJ, TRVI, LMNX, MGNX, BHVN,
OBE, AVTX — frozen source order, frozen case ids, one shared frozen boundary of
`2026-07-18T13:37:55.017661Z`.

**Verified IBKR historical source artifacts.** 26 private artifacts, re-hashed offline this
batch: 0 mismatches.

**Operation-specific admissibility.** Rather than one global "is this data good enough?",
the system asks per operation. Price *ratios* are admissible because a split factor cancels;
absolute price *levels* are not, because they do not. That distinction is what makes a
partial evaluation honest instead of overclaiming.

**Frozen Phase 3A requests and results.** 13 requests and 13 results, each serialized,
hashed, and byte-length recorded.

**Leakage protection.** 13 of 13 leakage audits passed. Forward-window and outcome
artifacts are hard-blocked at the file reader, and the "was anything forbidden opened?"
flags are computed from an actual access log, not asserted.

**Deterministic tests and artifacts.** 2,319 tests passing, synthetic fixtures only in
the repository; no licensed provider value is committed.

---

## What the current evaluation can honestly say

**Which rules are evaluable — 3 of 25.**

| Rule | Result across 13 cases |
| --- | --- |
| `MARKET_DATA_AVAILABLE` | `PASS` ×13 |
| `COMPLETED_BAR_AVAILABLE` | `PASS` ×13 |
| `PERCENTAGE_CHANGE_MINIMUM` | `PASS` ×6, `FAIL` ×7 |

**Which rules remain unknown — 22 of 25.** Two are blocked on unresolved provider semantics
(price band, relative volume). Thirteen are blocked because the evidence was never collected
at detection time (float, seven short-pressure rules, five catalyst rules). Seven are
evidence-validity meta-rules, six of which the evaluator could answer; one
(`REQUIRED_DOMAINS_PRESENT`) answers `FAIL` — meaning *the evidence request itself is
incomplete*, not that a candidate failed.

Across 325 rule-case pairs: 97 `PASS`, 20 `FAIL`, 208 `UNKNOWN`.

**Missing evidence was not fabricated.** No null became zero, no current value was dressed
as historical, no synthetic value entered a real case, no metric was invented. Committed
tests assert each of these individually.

**The system distinguishes availability and readiness from predictive validity.** "We have
the data" and "the rule fired" and "the rule predicts something" are three separate claims,
and only the first two are currently supported by anything.

**These are research evaluations, not trading recommendations.** No score, rank,
recommendation, target, or P&L field exists anywhere in the data model — enforced by a
structural validator, not by convention.

---

## Current limitations

**Weekend boundary.** The frozen detection boundary falls on a Saturday. The detection
context covers the preceding trading period; the forward window immediately after it is not
a trading window.

**No valid forward-outcome data.** Batch 02 established there is no lawful,
non-authenticated source for the forward outcome windows. The Batch 05 forward artifacts
exist but remain rejected and have never been opened. So there are no outcome labels at all.

**Unresolved volume semantics.** IBKR's official documentation is silent on the volume unit
and on corporate-action handling for volume, and the feed is disclosed as filtered. Every
volume-dependent operation therefore stays blocked rather than guessed.

**Missing float, short-pressure, and catalyst evidence.** Thirteen of the 25 rules have no
detection-time evidence of any kind. This is the single largest gap in the study.

**No predictive validation.** With no outcome labels, no statement about predictive
performance is possible, and none is made.

**No P&L, backtest, alerts, or trading.** None of these exist in the system and none were
built.

**Two disclosed modeling assumptions.** (1) Because the point-in-time engine gates on when
the *application* received data, and this is a reconstruction where the application received
it days later, receipt is modeled as the provider-availability instant; the alternative
literal reading is also computed and reported, under which the three evaluable rules move to
`UNKNOWN`. (2) The percentage-change window is the whole definitely-completed detection
window, not the original platform's intraday reference, because session boundaries are
unevidenced.

---

## The concrete next decision

**Approve, or not, a Phase 3B registry revision that references the new frozen Phase 3A
evaluations while retaining all 13 cases as outcome-incomplete and explicitly
non-predictive.**

What approval would mean: the registry gains a stable, hashed pointer to each case's frozen
Phase 3A request and result, so later work can cite exactly what was evaluated and when.

What approval would **not** mean: no outcome is acquired, no case is labelled, no rule
outcome is treated as a prediction, and the global data preflight stays rejected.

Everything needed for that revision is already frozen and verified. Nothing is blocked on
further engineering — only on your decision.

---

### If you want to look at one thing

`REQUIRED_DOMAINS_PRESENT = FAIL` on all 13 cases. It is the system correctly reporting that
it holds market bars and nothing else. Whether the next effort goes toward acquiring the
missing short-pressure and catalyst evidence, or toward resolving the volume semantics that
block two more rules, is the substantive research question underneath this batch.
