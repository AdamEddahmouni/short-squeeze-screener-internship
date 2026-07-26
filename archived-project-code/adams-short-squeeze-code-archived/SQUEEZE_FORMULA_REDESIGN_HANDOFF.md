# Squeeze Formula Redesign — Handoff for Planning

**Status: DONE — implemented and live-verified 2026-07-17.** The design questions in §4 were
resolved with the user (see the resolutions below) and the redesign shipped: all 248 tests pass
and the pipeline was verified end-to-end in the browser against fabricated KLRS/BIYA/LBGJ-style
data reproducing the advisor's complaints. The sections below are preserved as the original
planning context and the record of what was decided; treat §5's sketch as *implemented*, not
proposed. Don't re-plan this from scratch — if revisiting, the only open work is recalibrating the
thresholds/weights (all explicitly commented in `core/squeeze_score.py` as starting points) once
more live data accumulates, not re-architecting.

**How §4's open questions were resolved (2026-07-17):**
1. A new composite (`core/squeeze_score.py::classify_tier()`) became the Prime/Subprime gate;
   `core/scoring.py::score_setup()` is unchanged and now used *only* for cross-provider
   corroboration, preserving that data's meaning.
2. Prime = squeeze_score ≥ 70 AND short_float ≥ 5%; Subprime = 40–69 (starting values, commented
   as unvalidated).
3. TTM Squeeze folded in as a state-based composite component (`squeeze_on` → 100, off+positive
   momentum → 60, else 0); weight 20 of a 75 base.
4. `squeeze_confirmed` shipped with the sketched relvol ≥ 5 / |change%| ≥ 50 / TTM-momentum-
   confirming rule as an explicitly-tunable default.
5. `sentiment_mismatch` stays a `quality_flags` entry, not a scoring input (as recommended).
6. `tests/evaluate_historical_squeezes.py` built with researched, cited figures (GME/AMC solidly
   sourced; KOSS/BBBY flagged lower-confidence — no fabricated numbers).
7. No migration of old backtest data (gitignored, near-empty); Track Record panels start fresh
   from the cutover.

**Written:** 2026-07-17. **Implemented:** 2026-07-17.

*(Original planning instruction, now historical: "First action in the fresh session: enter plan
mode and design the approach before touching any code." This was followed — the plan was approved
before implementation. Kept here for the record.)* This touches the single most load-bearing
piece of logic in the app (see §3), used by every provider, both backtests, and both Track Record
panels.

## 1. Why this exists — the advisor's own words

From an advisor meeting on 2026-07-17 (auto-transcribed; a long garbled "squish squish squish..."
run in the middle is a transcription artifact, not content, and has been stripped from the quotes
below). The advisor was looking at the live app during the call. Cleaned, in order:

> "Your expectation is KLRS is prime. But sentiment is neutral."

> "BIYA shot up this morning about 4am... going up drastically... but at the same time the short
> interest was low and I don't know why."

> "LBGJ, the change is 13%. Usually when the squeeze happens it goes up, should be closer to 80,
> 90, 100, 200, 300 — something."

> "The gentleman who did this last summer used some criteria to do it. You may want to revisit
> those criteria and see whether they're solid. Maybe you have your own criteria that works
> better. The entire idea is we want to make sure we catch them sooner than anybody else."

> "The IB borrow fee is zero — if the borrow fee is nothing, then... the borrowing fee is one of
> the formula members that identifies the short squeeze. The higher the borrowing fee, the higher
> the short squeeze possibility. But if you don't have the borrowing fee, then it doesn't seem to
> work."

> "Do you have a TTM squeeze, or can you put that as a column so we can do sorting?"

> "You can actually ask AI which of the tickers are actually facing a short squeeze. With that in
> mind, you can potentially see how you can tweak the formula to match that kind of behavior."

> "BIYA — can you give me TTM squeeze on BIYA? That's not really a squeeze."

> "Can you give me a squeeze on the top one, LBGJ... You could say this is a squeeze, we want to
> see them and sort them. We don't want to open them one by one — that's too late. When the short
> squeeze happens, you really need to be in the market on time."

> (Closing) "I'm happy you are moving in the right direction. We just need to see how we can
> relate that to the market."

**Read that closing line carefully.** The user's first reaction to this meeting was "we need to
rebuild this all from the ground up" — that is **not** an accurate read of the transcript, and
should not be treated as the actual scope. The advisor's own words are asking for the
classification formula to be revisited and validated against real market behavior, not for a
rewrite. Push back gently on "rebuild from scratch" framing if it resurfaces; the fix described
here is scoped and additive to the existing architecture.

## 2. What was already verified true, same day, before this document was written

- IB Gateway and Schwab were both confirmed live and corroborating each other in real time
  (`source: ib` on every row, `corroborated_by: ['schwab']` on most).
- The IB borrow-fee FTP feed (`ftp3.interactivebrokers.com:21`) was confirmed genuinely
  unreachable at the network/TCP level (not an app bug) via a raw `socket.create_connection` test
  that timed out. This directly explains the advisor's "borrow fee is zero" observation for that
  session. It may or may not still be down — re-check before assuming it's still the cause.
- `core/squeeze_score.py`'s handling of a missing input (e.g. borrow fee) is mathematically
  correct: it excludes the missing component and renormalizes the remaining weights rather than
  treating it as zero (`_saturating_linear_score` returns `None` for `None` in,
  `compute_squeeze_score` renormalizes over whatever's `not None`). This is **not** a bug to fix —
  but it is currently invisible in the UI when *every* row is missing the same component
  system-wide (looks identical to "borrow fee just happens to be irrelevant here" vs. "the entire
  feed is down"), which is worth distinguishing.
- Example real row that day: `KLRS` — `squeeze_score: 38.5`,
  `squeeze_score_breakdown: {short_float: 13.9, borrow_fee: None, days_to_cover: 100.0}`. Useful
  as a concrete before/after test case once the new formula exists.

## 3. Current architecture — read this before touching anything

### 3.1 The actual Prime/Subprime gate is `core/scoring.py::score_setup()`

```python
def score_setup(price, change_percent, rel_volume, short_float_percent):
    score = 0
    if 2 <= price <= 20: score += 1
    if change_percent >= 10: score += 1
    if rel_volume >= 5: score += 1
    if short_float_percent >= 5: score += 1
    return score
```

4/4 = Prime, 3/4 = Subprime, otherwise dropped. **This is the whole classification gate.** It is
called from four places, and all four need to move together if the rubric changes:

- `core/filters.py:98` (`rank_and_group_stocks()`, the legacy Finviz-only path)
- `core/ib_api.py:208` (`rank_and_group_stocks_ib()`)
- `core/schwab_api.py:454` (`rank_and_group_stocks_schwab()`)
- `core/schwab_api.py:533` (Schwab-side rescoring used **only** for cross-provider corroboration —
  see §3.4, this one matters a lot)

**Critically, `score_setup()` never looks at borrow fee, days-to-cover, or TTM Squeeze at all.**
It's a price/momentum/liquidity/short-float screener, not a squeeze-mechanics detector. That gap
is the direct cause of the advisor's LBGJ/BIYA complaints (§1).

### 3.2 The separate 0-100 Squeeze Score — `core/squeeze_score.py`

A completely separate composite, built 2026-07-16, combining `short_float_percent` (weight
25/55), `ib_borrow_fee_rate` (20/55), `days_to_cover` (10/55) with saturating-linear sub-scores.
**This plays no role in Prime/Subprime classification.** A ticker can be labeled Prime with a
Squeeze Score near zero, and vice versa — they are two independent numbers computed from
overlapping but not identical inputs, and the advisor is very likely reacting to that mismatch
without knowing two separate formulas exist.

`compute_squeeze_score_breakdown()` returns the three sub-scores for the detail-panel UI.
`_WEIGHTS` and `_SATURATION` are both explicitly commented as calibrated-by-judgment, not
statistically derived — free to revise.

### 3.3 TTM Squeeze exists, and was deliberately excluded from scoring

`core/technical_indicators.py::compute_ttm_squeeze()` returns `(squeeze_on: bool | None,
momentum: float | None)`. Read the comment at lines 73-77 verbatim — it explicitly states TTM
Squeeze was kept **"display-only... not a Prime/Subprime scoring criterion... changing that
rubric's validated behavior is out of scope"** as a deliberate past decision. The advisor's "do you
have TTM squeeze, can you put that as a column, that's not really a squeeze" feedback (§1) is
**direct pushback on exactly that decision** — he's telling you it should inform classification,
not just decorate a badge.

Also important, from the same code comment: **`momentum`'s exact magnitude is not reliable** —
only its sign (direction) and the `squeeze_on` boolean (compression state) are the trustworthy
parts. Any new formula work should treat momentum as a sign/direction signal, not scale a weight
by its raw value.

Currently rendered as a non-sortable badge: `static/index.html:38` has `<th scope="col">Squeeze</th>`
with no `data-sort` attribute, unlike every other column in that table (`data-sort="..."
class="sortable"`). This is the literal thing the advisor asked for and doesn't have.

### 3.4 Cross-provider corroboration reuses `score_setup()` — changing the gate changes corroboration's meaning

`controller.py::_apply_corroboration()` (line 215) and `schwab_api.py:533` rescoring Schwab's own
numbers against the **same** `score_setup()` rubric is how `corroboration_score` (0-4) is
computed today (see `CROSS_PROVIDER_CORROBORATION_PLAN.md` §3.1 for the original design reasoning
— it deliberately reuses this exact rubric rather than inventing a separate one). **If
`score_setup()`'s criteria change, corroboration's meaning changes with it**, and so does every
already-collected row in `data/corroboration_history.csv` and `data/corroboration_outcomes.csv`
(scored under the old rubric). This needs an explicit decision in planning, not a silent
side-effect — see §5.

### 3.5 The shared positional row tuple — the change will need to thread through in lockstep

`controller.py::classify_batch()` (line 306) builds one ordered field list per stock, consumed
identically by:
- `ui/view.py`'s Tkinter `Treeview` (`columns = [...]` list, `ui/view.py` ~line 82, positional)
- `controller.py::get_snapshot()`'s `to_contract()` (line 396), which unpacks the same tuple into
  the schema-v1 JSON served by `api_server.py`

Any new field (e.g. a `squeeze_confirmed` flag, a `sentiment_mismatch` flag) needs a slot in
**all three** places in the same position, or one consumer silently breaks while another looks
fine. This exact mistake was made and caught by the full test suite once already this project
(see `PROJECT_NOTES.md`/session history around the `squeeze_score_breakdown` addition, 2026-07-17
— inserting a field shifted a `test_snapshot_carries_squeeze_score` negative index and required
padding two other test row fixtures). Expect the same category of breakage here; run the full
suite before considering any change done.

### 3.6 Everything downstream that keys off `setup_tier` / `squeeze_score` today

Changing the classification formula has a wide blast radius. All of the following read
`setup_tier` and/or `squeeze_score` as ground truth and will behave differently once the formula
changes — decide in planning whether that's intended (a formula fix *should* change these
outputs) or whether historical data needs to be labeled/segmented by which formula version
produced it:

- `tests/evaluate_squeeze_score_outcomes.py` + `core/squeeze_score_track_record.py` (Squeeze Score
  backtest, web UI panel)
- `tests/evaluate_corroboration_outcomes.py` + `core/corroboration_track_record.py`
  (corroboration backtest, web UI panel — doubly affected per §3.4)
- `tests/evaluate_target_stoploss_outcomes.py` (keys off `prime_log.csv`, which only logs Prime
  rows)
- `core/squeeze_score_history.py` / `core/corroboration_history.py` (per-cycle logging, feeds the
  above)
- `static/app.js`'s stats strip (Prime/Subprime counts, avg Squeeze Score, top setup) and Trend
  sparkline column
- The scheduled daily task that runs all three evaluators (`squeeze-score-backtest-evaluators`,
  see `mcp__scheduled-tasks__list_scheduled_tasks`)

## 4. Open design questions — resolve these during planning, don't silently assume

1. **Does `score_setup()` get replaced, or does a new function sit alongside it?** Four call sites
   currently share it (§3.1); a new squeeze-specific rubric could either replace this function's
   body (simplest, but changes corroboration's meaning per §3.4) or become a new function with
   `score_setup()` kept for whichever role makes sense (e.g. as a cheap first-pass liquidity
   filter before a heavier squeeze-specific score decides the tier). Needs a decision, and the
   decision needs to be explicit about what happens to corroboration (§3.4).
2. **Exact Prime/Subprime thresholds off the new formula.** The user's prior conversation (before
   this document existed) sketched Prime = Squeeze Score ≥ 70 with short float ≥ 5% as a floor,
   Subprime = 40-69 — these are starting numbers, not validated. Calibrate against §4.6 before
   locking them in.
3. **How to weight TTM Squeeze in the composite**, given momentum's magnitude isn't reliable
   (§3.3). A state-based score was sketched (`squeeze_on=True` → 100, `squeeze_on=False` +
   momentum > 0 → 60, else 0) — reasonable starting point, not validated.
4. **What `squeeze_confirmed` (a proposed new "is this actively squeezing right now" flag,
   independent of tier) should actually require.** Sketch: rel volume ≥ 5 AND |change%| ≥ 50 AND
   TTM momentum confirming breakout. The 50% figure is a guess calibrated loosely off the
   advisor's "80, 90, 100, 200, 300" comment — needs real calibration, not a guess kept as-is.
5. **Sentiment-mismatch handling** — a visible flag when tier is Prime but sentiment is
   neutral/negative (addressing the KLRS complaint in §1) was proposed as a `quality_flags` entry,
   not a scoring input. Confirm sentiment should stay out of the actual score (it's a noisy,
   independently-replaceable signal per `INCLUDE_SENTIMENT_OUTPUT`, see
   `ADVISOR_SUMMARY.md`) rather than folding it into the gate.
6. **How to build the historical-squeeze calibration check** the advisor himself suggested ("ask
   AI which tickers are actually facing a short squeeze, tweak the formula to match"). Proposed:
   a small offline test using known documented squeezes (GME Jan 2021, AMC mid-2021, KOSS Jan
   2021, BBBY Aug 2022) with their approximate pre-breakout short float / borrow fee /
   days-to-cover figures, confirming the new formula would have scored them highly **before** the
   move using only data available at that time — not the existing Track Record backtests, which
   only check whether *this app's own live picks* performed well afterward. Open questions: where
   do the historical reference numbers come from (need real, defensible sourcing, not invented
   figures — this is exactly the kind of claim that should never be fabricated), and does this
   live as a new `tests/` script, a new `core/` module, or documentation only?
7. **Backward compatibility of already-collected backtest data** (§3.6) — once the formula
   changes, do `data/squeeze_score_outcomes.csv` / `data/corroboration_outcomes.csv` rows scored
   under the old rubric get discarded, kept but flagged as pre-redesign, or does the Track Record
   panel just start fresh? These files are gitignored and currently near-empty (see
   `project_data_sources_status` history), so this is lower-stakes than it sounds, but still needs
   an explicit answer.

## 5. Suggested starting sketch — a starting point, not a mandate

(Proposed in the conversation that produced this handoff; not yet reviewed against the open
questions in §4.)

1. Fold TTM Squeeze into a new composite as a weighted, state-based input (§4.3).
2. Redefine Prime/Subprime off the composite score rather than the old 4-point gate; drop
   `change% ≥ 10` as a *qualifying* criterion (display-only going forward) since a modest price
   move is a symptom, not a squeeze-mechanics signal.
3. Add an independent `squeeze_confirmed` boolean/flag (§4.4), surfaced as its own sortable column
   — the direct answer to "we don't want to open them one by one."
4. Add a `sentiment_mismatch`-style quality flag (§4.5) rather than folding sentiment into scoring.
5. Surface a system-wide "borrow fee data currently unavailable" state distinctly from a normal
   single-ticker missing value (§2).
6. Build the historical-squeeze calibration check (§4.6) as the validation step, following this
   codebase's established "evidence over formula" pattern (see `tests/evaluate_squeeze_score_outcomes.py`
   for the pattern to mirror, though this one is calibration-against-history rather than
   backtest-against-the-future).

## 6. How this codebase verifies things — follow this pattern

Offline tests are necessary but this project does not consider them sufficient on their own —
every feature this project has shipped was also verified live. For this change specifically:

```
cd app/ScreenerProject
python -m pytest tests/ -q          # 219 passing as of 2026-07-17, before this change
python main.py                       # starts Tkinter + the API thread
```

Then in another shell: `curl http://127.0.0.1:8000/screener` and inspect real rows — confirm the
new fields/thresholds produce sane values against genuinely live IB/Schwab data, not just mocked
test fixtures. This project has caught real bugs this way that mocked tests alone missed (see
`CROSS_PROVIDER_CORROBORATION_PLAN.md` §6 for three prior examples). Do the same here: build,
test offline, then run live and sanity-check real tickers before calling it done.

**Deadline context:** the advisor's 2026-07-13 email set a 10-day operational deadline of
2026-07-23 for having both IB and Schwab "fully operational and bug-free" (already met — see
`project_advisor_data_source_priority` memory). This formula work is a quality/credibility
improvement on top of that, not itself gating the deadline, but land it with enough runway to
verify live before then.

## 7. What NOT to do

- Don't change `score_setup()`'s signature or behavior without updating all four call sites
  (§3.1) and deciding what happens to corroboration (§3.4) — don't let that be a silent
  side-effect.
- Don't add a new field to the classification output without threading it through all three
  consumers in the shared positional tuple (§3.5) — this has broken tests before in this exact
  project.
- Don't invent historical short-squeeze reference numbers (§4.6) without being transparent about
  the source and its precision — fabricated "ground truth" would undermine the entire point of
  calibrating against reality.
- Don't fold sentiment into the actual score (§4.5) without the user explicitly asking for that —
  it's designed to be an independently replaceable, optional signal
  (`INCLUDE_SENTIMENT_OUTPUT=false`), and coupling it into scoring works against that.
- Don't treat "we need to rebuild this from the ground up" as the actual scope — re-read §1's
  closing quote. This is a formula and criteria revision, not a rewrite.
- Don't skip live verification (§6).

## 8. Where to find more context

- `ADVISOR_SUMMARY.md` — current one-page state of the whole project, presentation script,
  honest-limitations section.
- `PROJECT_NOTES.md` / `RESEARCH_LOG.md` — full technical history, §-numbered.
- `CROSS_PROVIDER_CORROBORATION_PLAN.md` — the template this document follows, and required
  reading for §3.4's corroboration-reuse concern.
- Claude's persistent memory (if using Claude Code with memory enabled) has entries on advisor
  priorities and the data-source deadline — worth checking for anything that's shifted since this
  document was written.
