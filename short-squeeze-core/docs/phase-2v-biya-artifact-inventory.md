# Phase 2V BIYA Artifact Inventory

Forensic inventory of every locally discoverable artifact bearing on the BIYA
candidate event. Built before any Phase 2V runtime implementation, per the Phase 2V
design-first requirement.

Paths are given relative to the **workspace root** (the directory containing both
`short-squeeze-core` and `archived-project-code`), written as `<workspace>/...`. No
absolute local path appears in this document, and none may appear in any public
export. Every artifact below is **outside** `short-squeeze-core` and is read-only
forensic evidence.

## 1. Search method and scope

Two independent sweeps were run over the entire workspace, excluding `.git/`,
`.venv/`, `node_modules/`, `__pycache__/`, and pytest temp directories:

1. A ripgrep content search for `BIYA`, case-insensitive.
2. A PowerShell `Select-String` sweep over every file, used as a cross-check.

**The two sweeps disagreed, and the disagreement mattered.** Ripgrep reported five
matching files and silently skipped `app.log` — the single most important artifact —
because that file contains bytes ripgrep classifies as binary (mojibake from
mixed UTF-8/CP-1252 emoji logging). The PowerShell sweep found it. Any future
artifact search in this project must not rely on ripgrep alone.

Also searched, with no BIYA match: all `.zip` archives, `.pkl` models, `.db`/`.sqlite`
files, `.png` assets, the reconstruction source material, and every rebuilt-repo
fixture. No screenshot, database record, Mongo export, cached API response, or
saved candidate row containing BIYA exists anywhere in the workspace.

## 2. Artifact register

Reliability classes are those named in the Phase 2V design: `DIRECT_PLATFORM_RECORD`,
`DERIVED_FROM_PLATFORM_RECORD`, `EXTERNAL_CORROBORATION`, `FILESYSTEM_METADATA_ONLY`,
`USER_RECOLLECTION`, `UNKNOWN`.

### ART-001 — application log (the only direct platform record)

| Field | Value |
| --- | --- |
| `artifact_type` | `APPLICATION_LOG` |
| `relative_path` | `<workspace>/archived-project-code/adams-short-squeeze-code-archived/app/ScreenerProject/logs/app.log` |
| `content_hash` | `sha256:9cbd7d0c88956e6ce8350078ca9c4f6f029a3045655d5c6069a00c4821d66129` |
| `size_bytes` | 1007929 |
| `created_time_if_known` | `2026-07-17T10:23:58` (America/New_York, filesystem) |
| `modified_time_if_known` | `2026-07-17T12:54:58` (America/New_York, filesystem) |
| `embedded_event_time_if_known` | **none — the log carries no timestamps at all** |
| `reliability_class` | `DIRECT_PLATFORM_RECORD` |
| `sensitive` | **yes** |
| `included_in_public_demo` | no (a redacted derivative is) |

BIYA appears on 43 lines. **Every one of those 43 lines is a failure record.** They
fall into exactly two shapes:

- IB API `Error 10089` — *"Requested market data requires additional subscription for
  API… Delayed market data is available."* — carrying the real IB contract for BIYA:
  `conId=900208122`, `exchange='SMART'`, `tradingClass='SCM'` (NASDAQ Small Cap).
- Schwab cross-provider corroboration `HTTPSConnectionPool` failures, with
  `NameResolutionError` on `api.schwabapi.com` — DNS resolution failed outright.

The log therefore establishes exactly three facts, and no more:

1. BIYA was a real, resolved instrument in the platform's screening universe on
   2026-07-17 (a genuine IB contract lookup — this was **not** fabricated test data).
2. The platform could not obtain subscribed IB market data for BIYA and fell back to
   **delayed** data.
3. Schwab corroboration was entirely unavailable during the run.

The log contains **no** BIYA field value: no price, no percentage change, no relative
volume, no float, no short float, no short interest, no days to cover, no borrow fee,
no news, no score, and no Prime/Subprime label. Searches for `Prime`, `Subprime`,
`squeeze_score`, `score_setup`, `days_to_cover`, and `short_float` return zero hits in
the entire file.

The observed screening universe on the corroboration calls was
`KLRS, BIYA, SG, LBGJ, TRVI, SLS` and later `KLRS, BIYA, SG, TRVI, SLS` — BIYA is
present in both, LBGJ drops out of the second.

> **Sensitivity.** This log contains a live Finviz Elite API credential in a query
> string (`elite.finviz.com/news_export?...auth=<redacted>`). It is redacted from every
> Phase 2V fixture, export, and document, and **must not** be committed anywhere. The
> credential should be rotated independently of this phase.

### ART-002 — advisor meeting transcript

| Field | Value |
| --- | --- |
| `artifact_type` | `MEETING_TRANSCRIPT` |
| `relative_path` | `<workspace>/advisor-meetings.txt` |
| `content_hash` | `sha256:2636e2c314230b95e42c3709553f50b44221819be6ad049cbb645de5ec78b163` |
| `modified_time_if_known` | `2026-07-18T13:08:30` (America/New_York, filesystem) |
| `embedded_event_time_if_known` | `2026-07-17T12:46:15` — from the in-document recording filename `20260717_124615.mp4` |
| `reliability_class` | `DERIVED_FROM_PLATFORM_RECORD` (a transcript of a session in which the platform was on screen) |
| `sensitive` | yes (names a real individual) |
| `included_in_public_demo` | no (sanitized quotations only) |

The recording filename is the **single strongest detection-time anchor in the entire
workspace**: it is a machine-generated name encoding the recording start, and it is
independent of any filesystem timestamp.

This transcript records the advisor observing BIYA live in the application. The
substantive BIYA statements are:

> "`BIYA` rose sharply this morning at approximately 4:00 a.m. … the percentage change
> confirms that the stock has been moving upward significantly. However, its short
> interest appears to be low, and I am not sure why."

> "For example, can you retrieve the TTM Squeeze result for `BIYA`? … That stock may
> not actually be experiencing a squeeze."

Both statements are **negative or confused assessments**. Neither describes BIYA as a
validated success. See §4.

### ART-003 — contemporaneous redesign handoff

| Field | Value |
| --- | --- |
| `artifact_type` | `PROJECT_DOCUMENT` |
| `relative_path` | `<workspace>/archived-project-code/adams-short-squeeze-code-archived/SQUEEZE_FORMULA_REDESIGN_HANDOFF.md` |
| `content_hash` | `sha256:5a06f9b5ed0f85b910021d0470e390f6855b19798e4a9633b92a212def01d47e` |
| `modified_time_if_known` | `2026-07-17T14:21:02` (America/New_York) |
| `reliability_class` | `DERIVED_FROM_PLATFORM_RECORD` |
| `included_in_public_demo` | partial (its §3.1 finding, sanitized) |

Written **after** the meeting the same day. Independently corroborates the root cause
this phase reaches from code:

> "`score_setup()` never looks at borrow fee, days-to-cover, or TTM Squeeze at all. It's
> a price/momentum/liquidity/short-float screener, not a squeeze-mechanics detector."

It also records that the post-meeting redesign was verified against **fabricated**
KLRS/BIYA/LBGJ-style data. That fabricated data is a *later* verification input and is
**not** evidence about the original BIYA event. It does not appear in ART-001.

### ART-004 — archived repository git history (read-only)

| Field | Value |
| --- | --- |
| `artifact_type` | `VERSION_CONTROL_HISTORY` |
| `repository_or_source` | `adams-short-squeeze-code-archived` @ `0897562e…`; submodule `app/ScreenerProject` @ `6dbefd1a…` |
| `reliability_class` | `DIRECT_PLATFORM_RECORD` |
| `included_in_public_demo` | yes (commit subjects and times only) |

Commit authorship times are recorded by git at commit time and are far stronger than
filesystem metadata. The `ScreenerProject` submodule history for 2026-07-17
(America/New_York) brackets the meeting precisely:

| Commit | Local time | Subject | Relation to meeting |
| --- | --- | --- | --- |
| `6f0c201d` | 10:31:34 | Localize timestamps in the web UI's detail panel | before |
| `05c81f85` | 10:42:26 | **Rename "Short Float %" column to "Short Interest %"** | before (−2h04m) |
| `5a603fc8` | 10:48:13 | `Cache-Control: no-cache` on static files | before |
| `e0b9404b` | 11:16:21 | Backtest corroboration; Squeeze Score breakdown | before |
| `94c83751` | 11:44:57 | SPY benchmark in Track Record panels | before |
| `b016d92f` | 11:56:43 | Sparklines, stats strip, alpha bars | **last commit before the meeting** |
| — | **12:46:15** | **advisor meeting begins (ART-002)** | — |
| `5a0f6eb4` | 15:39:27 | **Redesign Prime/Subprime around a squeeze-mechanics composite** | after (+2h53m) |
| `24319ca9` | 2026-07-18 12:47:17 | TTM Squeeze fire detection | after |

**Therefore the code state the advisor observed is `b016d92f`,** not the archived
working-tree HEAD. This is the most consequential finding in the inventory: the
archived checkout is the *post-redesign* code, and reconstructing the original rules
from it would describe logic that did not exist when BIYA was surfaced.

### ART-005 — reconstruction timeline and traceability index

| Field | Value |
| --- | --- |
| `artifact_type` | `DERIVED_SUMMARY` |
| `relative_path` | `<workspace>/short_squeeze_project_reconstruction/03_project_timeline.csv`, `…/05_source_traceability_index.md` |
| `content_hash` | `sha256:1247975d…d4d087`, `sha256:822a53f9…1d34c7` |
| `reliability_class` | `DERIVED_FROM_PLATFORM_RECORD` |
| `included_in_public_demo` | no |

Both are Phase 0 derivatives of ART-002, not independent observations. They date the
review to 2026-07-17 and summarize it as *"KLOS, BIYA, and LBGJ examples expose
mismatch between Prime/Subprime labels and market reality."* Note these render the
first ticker as `KLOS` where ART-001 and ART-003 render it `KLRS`; ART-001 (the
platform's own log) is authoritative, so `KLRS` is correct and `KLOS` is a
transcription artifact. This is recorded because it demonstrates that the transcripts
are lossy on ticker symbols.

### ART-006 — advisor email log

| Field | Value |
| --- | --- |
| `artifact_type` | `EMAIL_LOG` |
| `relative_path` | `<workspace>/email-log.txt` |
| `content_hash` | `sha256:ae8ae37233230133e08e822affa340878e09c8153f899ae5e40338c6629abb45` |
| `reliability_class` | `EXTERNAL_CORROBORATION` |
| `sensitive` | yes (personal name, personal correspondence) |
| `included_in_public_demo` | no |

Contains six messages spanning 2026-07-06 to 2026-07-17. **It contains no mention of
BIYA and no message later than 2026-07-17.** See §4.

## 3. Absent artifacts (recorded as gaps, not filled)

The following were searched for specifically and **do not exist** in the workspace.
None is reconstructed, estimated, or substituted:

| Missing artifact | Consequence |
| --- | --- |
| Any saved BIYA candidate row, snapshot, or score-history record | Every original BIYA field value is `UNKNOWN` |
| Any screenshot of the application showing BIYA | No visual corroboration of displayed values |
| Any MongoDB export, SQLite database, or JSON snapshot containing BIYA | No persisted candidate state |
| Any cached Finviz/IB/Schwab API response for BIYA | No provider payload to replay |
| Any BIYA market bar, quote, or trade record, at any interval, on any date | **No outcome observation is computable** |
| Any BIYA news item, headline, or publication timestamp | News timing audit is structural only |
| Any BIYA short-interest or borrow record | Days-to-cover cannot be recomputed for BIYA |
| The advisor email reporting that BIYA squeezed | See §4 |

## 4. The premise conflict, recorded as evidence

The Phase 2V brief states that the advisor sent: *"Good news: BIYA squeezed up
yesterday as predicted by your platform."*

**No such artifact exists in this workspace.** ART-006 is the complete local email
record and ends on 2026-07-17 with no BIYA reference. This is recorded here as a
finding, not treated as a defect in the brief — the message may well exist outside the
workspace. But it cannot be used as evidence, and it is not assigned a reliability
class, because Phase 2V may not admit an artifact it cannot hash, date, or read.

Two consequences follow, and both are load-bearing for the case conclusion:

1. **The only recorded advisor statements about BIYA are negative** (ART-002): short
   interest "appears to be low," and "that stock may not actually be experiencing a
   squeeze." In the local record BIYA is an example of a *suspected defect*, not a
   validated success.
2. Even if the message is produced later, it could not retroactively validate the
   methodology. Per the Phase 2V rule classifications, a subsequent price move is an
   outcome observation; it is never evidence that the original rules were correct or
   that their inputs were available at detection.

This does not block the phase. It fixes the case conclusion at `INSUFFICIENT_EVIDENCE`
and moves the outcome observation into the acquisition manifest.

## 5. Detection-time evidence derived from this inventory

Two different questions have two different answers, and conflating them would overstate
precision:

| Question | Window (America/New_York) | Window (UTC) |
| --- | --- | --- |
| **When was BIYA surfaced by the screener?** | `10:23:58` – `12:54:58` | `14:23:58Z` – `16:54:58Z` |
| When was BIYA *observed and discussed* on screen? | `12:46:15` – `12:54:58` | `16:46:15Z` – `16:54:58Z` |

**The resolved `DetectionTimeEvidence` uses the first**, because Phase 2V asks when the
platform surfaced the candidate, not when a human commented on it:

| Field | Value |
| --- | --- |
| `state` | `BOUNDED_TIME_WINDOW` |
| `window_start` | `2026-07-17T14:23:58Z` (ART-001 creation — the screener run begins) |
| `window_end` | `2026-07-17T16:54:58Z` (ART-001 last write) |
| `source_artifact_ids` | ART-001, ART-002 |
| `confidence_basis` | Run start bounds below; log last-write bounds above; the recording filename independently confirms BIYA was on screen inside the interval |

BIYA's first log line is at file line 4, at the very start of a run beginning
`10:23:58` local — so it was surfaced essentially as soon as the screener started, well
before the meeting. Narrowing to the 8m43s meeting window would describe when the
advisor *spoke*, not when the platform *decided*, and would claim roughly 17× more
precision than the evidence supports.

`EXACT_TIMESTAMP` is **not** claimed. ART-001 carries no internal timestamps, so both
bounds rest on filesystem metadata, which the Phase 2V design forbids treating as a
direct platform event time. The resolved window is ~2h31m wide, and replay runs at both
edges precisely because that width is real.

One further caveat: the advisor's "rose sharply this morning at approximately 4:00 a.m."
describes BIYA's *price move*, not a platform detection event. It is not used as a
detection timestamp.
