# Meeting Talking Points — Phase 3B Registry Revision

One page. Every answer is tied to committed evidence.

---

**"What did you actually prove?"**

That 13 real, outcome-blind candidates can be carried through a full evidence pipeline —
acquisition, semantic resolution, admissibility, and a frozen Phase 3A evaluation — without
any leakage, and that the pipeline reports honestly when evidence is missing. 325 rule-case
evaluations exist, all 13 leakage audits pass, and no outcome was ever read. I did not prove
that the screener predicts anything.

**"What works now?"**

Data acquisition and preservation (26 hash-verified IBKR artifacts). Deterministic,
reproducible identity — every artifact regenerates byte-identically. Point-in-time discipline
— the frozen boundary is enforced and audited. Rule evaluation with explicit missing-evidence
handling. Both availability rules pass 26/26, so the acquired data is genuinely usable for the
operations it's admissible for.

**"Why are so many rules UNKNOWN?"**

Because the evidence for them does not exist in the data I have. Short interest, borrow fee,
borrow availability, float, news, and SEC filings were never acquired — 91 short-pressure and
65 catalyst evaluations have nothing to test against. `UNKNOWN` means "not testable", which is
different from `FAIL`, which means "tested and did not hold". Collapsing the two would
fabricate evidence and would quietly inflate or deflate every downstream rate.

**"Why can't you just use the IBKR values?"**

The numbers are there; their meaning isn't fully documented. IBKR's official documentation
confirms prices are split-adjusted, but is silent on whether volume is adjusted, on what an
intraday bar timestamp refers to, and on the volume unit. I resolved what the official
evidence supports and recorded the rest as unresolved rather than assuming. Ratios of prices
are unaffected by the unresolved parts, so those are admissible; absolute levels and volume
are not.

**"Why is PRICE_RANGE blocked?"**

It tests an absolute price level, and absolute-price admissibility is exactly what the
unresolved semantics block. It is one of three required rules for research detection. The
other two now pass for all 13 cases; this one resolves `UNKNOWN`, so detection resolves
`UNEVALUABLE`. I did not substitute `PERCENTAGE_CHANGE_MINIMUM` for it — that would be a
different predicate answering a different question, and a committed test forbids the
substitution.

**"Why don't you have outcomes?"**

The frozen boundary falls on a weekend. When I requested the forward 24-hour window, IBKR
returned the previous available Friday's bars — data from *before* the boundary, not after it.
Those are not forward-outcome evidence, so I rejected them rather than labelling outcomes from
pre-boundary data. There is currently no lawful non-authenticated source for the forward
windows I need.

**"Does this mean the screener works?"**

No, and nothing here should be read that way. Detection is `UNEVALUABLE` for all 13 cases and
there are no outcomes, so there is no confusion matrix, no hit rate, and no accuracy figure.
What exists is a reproducible evidence chain, not a performance claim.

**"Can this trade yet?"**

No. There is no backtest, no P&L, no threshold optimization, no scoring, no ranking, and no
recommendation anywhere in the codebase — structural tests refuse those field names outright.
The global preflight verdict is still `PREFLIGHT_REJECTED`. Nothing here is trading-ready and
nothing is claimed to be.

**"What do you need next?"**

One decision from you: whether to record the frozen Phase 3A evaluations in the Phase 3B
registry while leaving detection `UNEVALUABLE` and outcomes absent. Beyond that, the two real
blockers are (1) authoritative IBKR semantics for absolute price and volume — or an
alternative source with documented semantics — which would unblock `PRICE_RANGE`, and (2) a
lawful forward-window source, or a new cohort whose boundary does not fall on a weekend, which
would unblock outcomes. Until at least one of those moves, the honest state of the project is
"evaluation complete, detection and outcomes not".

---

**The one thing to remember:** *evaluation completeness*, *detection completeness*, and
*outcome completeness* are three different things. Batch 08 delivered the first. Batch 09 asks
only whether to record that fact in the registry. It does not deliver, or claim, the other
two.
