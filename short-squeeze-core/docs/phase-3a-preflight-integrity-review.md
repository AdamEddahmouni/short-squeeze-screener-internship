# Phase 3A Preflight Integrity Review

## Scope and conclusion

This review was completed before Phase 3A runtime implementation. It inspects the
preserved Phase 2V BIYA acquisition bytes, their committed normalized derivatives,
the Phase 1 market-bar normalization diagnostics, and the Phase 2V FINRA
short-sale-volume parser. No Phase 2V artifact or anchor was changed.

The review found no market-bar normalization bug. All 457 rejected intraday rows are
provider rows whose open, high, low, close, and volume entries are all null. Rejecting
them under the required-open contract is correct and preserves missingness. The
rejections do not intersect either detection boundary's 15-minute, 30-minute, or
one-hour window. Twenty-one rejected null rows occur during the next regular-session
close window, but neither the next-session opening bar nor the terminal close minute is
rejected. Those rows explain partial outcome-window coverage and are not eligible
Phase 3A detection inputs.

The FINRA parser maps the six pipe-delimited source columns directly and preserves the
three numeric volume fields as exact `Decimal` values. The acquired 2026 files contain
fractional share quantities in those fields. No ratio, scaling, delimiter conversion,
thousands-separator transformation, or fixture-generation step introduced the
fractions. FINRA daily short-sale volume remains venue-scoped transaction-volume
context and is not published short interest or a Phase 3A short-pressure input.

## Intraday rejection analysis

### Preserved inputs

- Acquisition: `ce9bd6bf-15d5-5343-9b4c-3d6fe51583ea`
- Provider: `yahoo-chart`
- Interval: one minute, regular and extended sessions
- Adjustment policy: `PROVIDER_ADJUSTED`
- Raw SHA-256: `sha256:069950d161fee020342b2677eb13a57aeea173f49e42adf9959352943c6ba6ce`
- Raw provider rows: 3,295
- Accepted observations: 2,838
- Rejected rows: 457
- Duplicate timestamps: 0

### Deterministic rejection breakdown

| Diagnostic code | Count | Source condition | Classification |
| --- | ---: | --- | --- |
| `BAR_MISSING_OPEN` | 457 | `open`, `high`, `low`, `close`, and `volume` are all null at the same timestamp | malformed/incomplete provider record |
| Duplicate bar | 0 | every raw timestamp is unique | not present |
| Conflicting bar | 0 | no duplicate key exists from which a conflict could arise | not present |
| Missing timestamp | 0 | all 3,295 rows have a timestamp | not present |
| Unsupported session classification | 0 | every timestamp maps deterministically to a supported session | not present |
| Missing or invalid volume as the primary rejection | 0 | volume is null on the same 457 rows, but required `open` fails first | contributory missing field, not a separate rejection |
| Out-of-range record | 0 | raw range is `2026-07-16T08:00:00Z` through `2026-07-21T21:00:09Z`, within the requested acquisition range | not present |
| Adjustment inconsistency | 0 | one provider-adjusted policy applies to the acquisition | not present |

The rejection count in `HistoricalMarketDataset.rejected_record_count` is obtained by
counting error diagnostics for which normalization did not continue. It therefore
matches the 457 provider rows exactly; it is not a count of every diagnostic attached
to those rows.

Rejected rows by UTC trade date:

| Date | Rejected rows |
| --- | ---: |
| 2026-07-16 | 359 |
| 2026-07-17 | 2 |
| 2026-07-20 | 33 |
| 2026-07-21 | 63 |

The two July 17 rejections occur at `19:16:00Z` and `19:35:00Z`, after both one-hour
detection-boundary windows.

### Critical-window intersection

Intervals use the Phase 2V half-open bar-selection convention: a row is inside a window
when its bar start is greater than or equal to the window start and strictly less than
the requested end.

| Critical interval | Rejected rows | Effect |
| --- | ---: | --- |
| Detection window, `14:23:58Z`-`16:54:58Z` | 0 | none |
| Earliest boundary 15 minutes | 0 | none |
| Earliest boundary 30 minutes | 0 | none |
| Earliest boundary 1 hour | 0 | none |
| Latest boundary 15 minutes | 0 | none |
| Latest boundary 30 minutes | 0 | none |
| Latest boundary 1 hour | 0 | none |
| Next-session opening bar, `2026-07-20T13:30:00Z`-`13:31:00Z` | 0 | none |
| Next regular-session close window, `13:30:00Z`-`20:00:00Z` | 21 | coverage remains partial; missing rows cannot contribute price or volume |
| Terminal close minute, `19:59:00Z`-`20:00:00Z` | 0 | terminal close observation is retained |

The 21 null rows inside the next-session close window can affect only the completeness
diagnostic and the unknowable volume that those missing rows might have contained.
They do not alter any retained observed price, and Phase 2V already marks the affected
window partial. Phase 3A evaluates BIYA at `2026-07-17T14:23:58Z` and
`2026-07-17T16:54:58Z`; later outcome rows are prohibited as detection inputs. Thus no
rejected row affects a Phase 3A rule input.

### Correction decision

No correction is made. Converting an all-null provider row into a completed bar would
invent price and volume evidence. The existing rejection is backward-compatible,
deterministic, and semantically correct. No corrected derivative dataset is needed.

## FINRA daily short-sale-volume decimal analysis

### Exact source mapping

The preserved raw files have this header:

`Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market`

`parse_finra_short_sale_volume()` splits the header and each row on `|`, zips values by
column name, selects the exact requested symbol, and maps fields as follows:

| Source column | Parsed field | Type and semantics |
| --- | --- | --- |
| `Date` | `trade_date` | calendar trade date parsed as `%Y%m%d` |
| `Symbol` | `symbol` | exact requested symbol |
| `ShortVolume` | `short_volume` | exact decimal aggregate short and short-exempt reported share volume |
| `ShortExemptVolume` | `short_exempt_volume` | exact decimal aggregate short-exempt reported share volume |
| `TotalVolume` | `total_volume` | exact decimal aggregate reported share volume |
| `Market` | `market_scope` | reporting-facility codes (`B`, `Q`, `N`) |

The three retained BIYA source rows are:

| Trade date | Short volume | Short-exempt volume | Total volume | Market scope |
| --- | ---: | ---: | ---: | --- |
| 2026-07-16 | 9003.650000 | 2244 | 19562.869194 | Q,N |
| 2026-07-17 | 6014433.017900 | 47223 | 10336898.305041 | B,Q,N |
| 2026-07-20 | 13226150.060678 | 526991.214221 | 23231974.145935 | B,Q,N |

The decimals exist in the immutable raw response bytes and are common across other
symbols in the same files. The normalized values differ only by canonical removal of
insignificant trailing zeros. They are not percentages: for each BIYA row, the values
occupy the documented volume columns, and the raw file contains no ratio or percentage
column. No scaling or thousands separators are present.

### Source semantics and fractional quantities

FINRA describes Daily Short Sale Volume as aggregated publicly disseminated,
off-exchange transaction volume reported to a TRF, ADF, or ORF. FINRA also states that
this data is not and is not intended to equal twice-monthly short-interest position
data. The preserved July 2026 source bytes carry decimal share quantities after
FINRA's February 23, 2026 fractional-share reporting enhancement took effect. That
enhancement permits fractional share quantities with up to six decimal places at the
trade-reporting boundary, consistent with the six-place fractions in these aggregates.

There is a documentation caveat: FINRA's linked legacy Daily Short Sale Volume File
Layout still says the three volume fields have no decimals. The observed 2026 source
files and the newer fractional-share reporting rules are more current than that 2011
layout, but this mismatch means the fractional aggregates must retain explicit source
provenance and must not be reinterpreted as whole-share counts. Relevant primary
sources:

- [FINRA Daily Short Sale Volume Files](https://www.finra.org/finra-data/daily-short-sale-volume-transaction-data)
- [FINRA Short Sale Volume data semantics](https://www.finra.org/finra-data/browse-catalog/short-sale-volume)
- [FINRA January 14, 2026 fractional-share reporting notice](https://www.finra.org/rules-guidance/notices/trade-reporting-notice-20260114)
- [FINRA legacy daily-file layout](https://www.finra.org/sites/default/files/DailyShortSaleVolumeFileLayout.pdf)

### Fixture-generation audit and correction decision

The Phase 2V anchor generator reads the committed raw bytes and calls
`parse_finra_short_sale_volume()`; it does not calculate or synthesize the volume
fields. The fixture serializer only applies canonical JSON formatting. The existing
synthetic parser test also uses decimal values deliberately, but it is not the source of
the historical BIYA fixture.

No normalization correction is made and no corrected derivative is produced. Exact
`Decimal` preservation is the least interpretive representation of the source. These
records remain excluded from Phase 3A short-pressure rules because daily short-sale
transaction volume is neither published short interest, short float, nor a valid
days-to-cover numerator.

## Integrity assertions

- Phase 2V raw acquisitions remain byte-identical.
- Phase 2V normalized derivatives remain byte-identical.
- The original and outcome-amendment anchor manifests remain unchanged.
- No archived repository was modified.
- No rejected provider row was repaired, defaulted, or backfilled.
- No FINRA short-sale-volume record is substituted for published short interest.
- No later BIYA outcome observation is admitted as a detection-time Phase 3A input.
