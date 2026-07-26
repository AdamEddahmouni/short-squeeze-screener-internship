# Fresh-Start Data and Short-Interest Plan

**Prepared:** 2026-07-12  
**Scope:** single non-professional user; local development/demo; no automatic trading  
**Constraint:** do not deposit $500 merely to activate paid IBKR data

## Executive conclusion

The project does **not** require a $500 Interactive Brokers balance to continue.

IBKR's current official pages establish three separate facts:

1. Individual IBKR Pro accounts have a **$0 account minimum** and **$0 inactivity fee**.
2. IBKR advertises **free real-time, non-consolidated Cboe One and IEX data for U.S.-listed stocks
   and ETFs**, but its API-specific documentation says free on-platform data is not necessarily
   available through the API and that live API data and historical bars require paid Level 1
   subscriptions. The user's observed delayed API data is consistent with that rule.
3. A normally funded balance of **$500 plus fees is required to activate paid market-data
   subscriptions**. The optional consolidated Network A/B/C add-on is $4.50/month for a qualifying
   non-professional subscriber.

The correct baseline is therefore a **zero-new-deposit non-IB-live path**, using the already
available Finviz Elite authorization. There is no supported way to promise complete live IB API
data from the user's present free/unfunded setup. Code defects still make the fallback behavior
worse: the app discards an IB row when historical bars fail before checking price fallbacks, and it
suppresses Finviz whenever IB is merely connected even if IB produces no usable rows.

Recommended design:

- use the already available Finviz Elite real-time export for market-wide discovery and the five
  required screening fields;
- use IB scanner/shortable-share fields only where the account actually returns them, with delayed
  or unavailable status explicitly reported; do not promise live IB enrichment without entitlement;
- calculate short float from the latest reported shares short and float shares, with source and
  `as_of` timestamps;
- retain yfinance and Finnhub only as labeled fallbacks;
- publish every 15 seconds while preserving each field's true source and cadence.

Paid IB Level 1 data is required if the professor specifically requires live data to come through
the IB API. It is not required if Finviz Elite is accepted as the live market-data source and IB is
kept as a scanner/broker integration path.

## 1. Requirements reconstructed from the project

The requested deliverable is a read-only U.S. short-squeeze screener that:

- runs locally and is ready for integration;
- refreshes close to real time (currently targeting 15 seconds versus the requested ~1 minute);
- screens price $2-$20, float below 20 million, change at least 10%, relative volume at least 5,
  and short float at least 5%;
- uses IB where useful, with other providers available as fallbacks or supplements;
- exposes a stable API/file contract;
- keeps sentiment optional and replaceable because separate development is underway;
- places no trades; and
- now includes a documented short-interest calculation throughout scoring, GUI, API, tests, and
  handoff documentation.

## 2. Short-interest definitions and formulas

### Primary calculated field

`shares_short` is the number of open short positions reported for a security on a settlement date.
FINRA requires firms to report it twice monthly; it is not an intraday feed.

The required primary calculation is:

```text
short_float_percent = (shares_short / float_shares) * 100
```

Validation rules:

- require `shares_short >= 0` and `float_shares > 0`;
- retain `shares_short_as_of` and `float_shares_as_of` separately;
- retain `short_interest_source` and `float_source`;
- return `null` plus a reason when either input is absent or invalid;
- compare a provider-supplied percentage with the local calculation and flag material differences;
- never silently substitute daily short-sale volume or broker inventory.

Finviz defines Short Float using the same shares-short divided by shares-float formula.

### Days to cover

Add a separate supporting field:

```text
days_to_cover = shares_short / average_daily_share_volume
```

FINRA uses this formula. The average-volume window must be documented.

### Daily short-sale volume ratio

If added later, label it `daily_short_sale_volume_percent`, not short interest:

```text
daily_short_sale_volume_percent =
    (short_sale_volume / total_reported_volume) * 100
```

FINRA explicitly warns that daily short-sale volume is not short interest and that FINRA daily
files are not consolidated with exchange files. It is optional context, not the primary filter.

### IB shortable shares

IB generic tick 236 is the quantity IB reports as available to borrow. It is broker-specific
inventory, not market-wide open short positions. Preserve it as:

```text
ib_shortable_shares
ib_shortable_shares_as_of
```

It may be useful as a live borrow-availability signal, but it must not be called short interest or
replace `shares_short` in the formula.

## 3. Fresh audit of every practical data route

### Interactive Brokers

An individual IBKR Pro account has a published $0 account-opening minimum, but that is separate from
market-data entitlement. IBKR's general pricing page advertises an included real-time
non-consolidated Cboe One/IEX feed. Its API-specific pages state that free on-platform data may not
be available off-platform through the API, and that live API market data and historical bars need
paid Level 1 subscriptions. For this project, the user's actual delayed API result is the decisive
operational evidence: the included display feed cannot be quoted as a working live API feed.

The $4.50 A/B/C subscriptions supply the relevant U.S. Level 1 coverage, but paid subscriptions
normally require $500 in account equity. Because the user will not fund that amount, real-time IB
API data is excluded from the baseline. Unsubscribed U.S. stock data in paper accounts is 15
minutes delayed, and trial accounts cannot receive real-time API data for most instruments.

### Finviz Elite

The project already has a working advisor-provided Elite credential/token. Finviz says Elite
includes real-time quotes and screener data, export/API access, and NYSE/Nasdaq/Amex coverage. Its
screener supplies price, change, float, relative volume, and Short Float. Finviz defines relative
volume as current volume divided by the three-month average, intraday adjusted.

This is the most complete no-new-deposit discovery source already available. Promote Finviz from a
connection-only fallback to the market-wide candidate generator; use IB for optional enrichment and
independent checks. This depends on continued authorization to use that single-user Elite account.
The receiving operator needs their own authorized credential if access does not transfer.

### Schwab Trader API

The advisor explicitly requires the full TD Ameritrade replacement through Schwab's Individual
Trader API. Schwab's official catalog says this personal-use product includes authentication,
real-time market data, account information, transactions, and trading capabilities. The project
must implement authentication and market data, but must not enable order placement because this
screener is read-only.

Prerequisites are a Schwab brokerage account, Individual Developer registration, product access,
an approved personal-use app, a registered callback URL, OAuth authorization, and token renewal.
Detailed endpoint specifications are visible only after Developer Portal sign-in; the repository
currently contains no Schwab code, configuration, or credentials.

Schwab should become a first-class provider alongside Finviz and IB. It must be validated for quote
freshness, history, movers/discovery coverage, stream behavior, rate limits, token lifetime, and
field completeness before it becomes the automatic primary source.

### Alpaca

Alpaca Basic is IEX-only and carries free-tier symbol/rate/history restrictions; the full U.S.
exchange feed is paid. It can be a quote fallback but does not improve on IB Cboe One/IEX for
market-wide discovery.

### Finnhub

Finnhub advertises free real-time REST/WebSocket access, and the app uses it as a last-resort price
fallback. Project testing hit free-tier limits when making per-symbol requests across a 50-stock
scan. Published paid market-data plans exceed the zero-new-cost target. Keep it sparse and optional.

### yfinance/Yahoo

yfinance supports screeners and most-shorted fields. Its documentation identifies it as an
unofficial open-source interface intended for research/educational and personal use. Keep it as a
cached, source-labeled fallback, not the sole integration contract.

### Alpha Vantage

Its free quote and top-gainer results default to end-of-day. Official documentation places
real-time and 15-minute-delayed U.S. endpoints behind premium entitlement. It is not a zero-cost
15-second solution.

### FINRA and listing exchanges

FINRA supplies the authoritative reporting definition, schedule, glossary, catalog, and API
documentation. Listing-exchange products such as NYSE Group Short Interest are semi-monthly. These
establish the correct inputs and cadence. Direct access/licensing for all required listed symbols
must be verified in the receiving runtime. Finviz's field can be used immediately while an official-
source adapter is built and compared.

### Cboe DataShop and shortsqueeze.com

Neither is necessary for the baseline. A Cboe product may help later options/order-flow research,
but it does not turn official short interest into a live metric. No evidence currently establishes
a superior zero-cost 15-second shortsqueeze.com API. Do not add either until a specific missing
field, price, license, and validation test are documented.

## 4. Concrete defects in the current implementation

These explain why the current run could appear to require paid IB data:

1. ~~**Historical-data hard gate.**~~ **Fixed 2026-07-13.** `core/ib_api.py::_build_row()` no
   longer returns `None` just because `_get_hist_stats()` failed - it now falls through to the
   live ticker/Finnhub price fallbacks first via `_hist_stats_or_degraded()`, only discarding the
   row if genuinely no price or prev_close source exists anywhere. RSI/weekly-volatility/relative-
   volume correctly stay unavailable (neutral defaults + an explicit `historical_bars_unavailable`
   quality flag) since those truly can't be computed without bars - but price/change% no longer
   need to be sacrificed along with them.
2. ~~**Connection is mistaken for usable data.**~~ **Fixed 2026-07-13.** `core/ib_api.py::
   is_ib_available()` (the function `controller.py`'s provider-priority dispatch now calls, see
   `PROJECT_NOTES.md` §9c) factors in enrichment health, not just the raw socket connection: a
   session that's connected but has 3+ consecutive passes where every raw scanner candidate fails
   to enrich (`_record_enrichment_result()`) is reported unavailable, correctly falling through to
   Schwab/Finviz. An empty *scored* result (zero Prime/Subprime matches) is still treated as valid
   and does not count as a failure - only a pass that produces zero usable *rows* from a non-empty
   raw candidate list does.
3. ~~**Borrow inventory is discarded.**~~ **Fixed 2026-07-13** (short-interest work, see
   `PROJECT_NOTES.md` §7) - tick 236 is now carried through as `ib_shortable_shares` end-to-end
   into ranking/GUI/API instead of being computed and thrown away.
4. **Float requirement is not enforced on the IB path.** Documentation requires float below 20
   million, but IB scoring treats float as display-only. Finviz applies it in its query.
5. **IB relative volume is not live intraday.** It uses the latest daily historical bar volume
   divided by an average, unlike Finviz's intraday-adjusted relative volume.
6. **Field provenance is missing.** Consumers cannot distinguish live, cached, fallback, and
   twice-monthly values.
7. **General pricing was confused with API entitlement.** IBKR's general pricing page advertises a
   free Cboe One/IEX display feed, but API-specific documentation says live API data and historical
   bars require paid subscriptions. The code gate is still a fallback bug, but fixing it will not
   create an IB entitlement the account does not have.

## 5. Recommended architecture

```text
Finviz Elite real-time screener (market-wide discovery + five required fields)
                              |
                              v
                 normalized candidate records
                              |
           +------------------+------------------+
           |                                     |
           v                                     v
IB data when actually entitled           short-interest adapter
+ labeled delayed/availability fields    (shares short + float + as-of)
           |                                     |
           +------------------+------------------+
                              v
            validation, scoring, provenance, freshness
                              |
                              v
       desktop GUI + atomic schema API + optional Mongo/Vercel mirror
```

Provider selection must be based on **field availability and freshness**, not connection status.

| Field | Primary | Secondary | Missing behavior |
|---|---|---|---|
| Candidate universe | Finviz Elite | IB scanner, then yfinance | Empty result + degraded health reason |
| Price/change | Finviz Elite | Entitled IB, then Finnhub/last close | Mark stale; never claim current |
| Relative volume | Finviz intraday-adjusted | Valid live cumulative volume + documented baseline | `null`; fail criterion |
| Float shares | Finviz | yfinance cached | `null`; fail criterion |
| Shares short | official/latest licensed semi-monthly source | Finviz-derived input if necessary | `null`; fail criterion |
| Short float % | local formula | Finviz supplied value | `null`; fail criterion |
| IB availability | IB tick 236 | none | Optional/null; never substitute |
| Sentiment | local model only when enabled | downstream replacement | Omit when disabled |

## 6. API/schema additions

Keep `short_float_percent` for compatibility and add explicit inputs/metadata:

```json
{
  "shares_short": 2500000,
  "float_shares": 15000000,
  "short_float_percent": 16.67,
  "days_to_cover": 2.5,
  "short_interest_as_of": "2026-06-30",
  "short_interest_source": "provider-or-exchange-name",
  "float_as_of": "2026-07-12T13:30:00Z",
  "float_source": "finviz",
  "ib_shortable_shares": 125000,
  "ib_shortable_shares_as_of": "2026-07-12T13:30:15Z",
  "market_data_source": "finviz+ib_free_non_consolidated",
  "observed_at": "2026-07-12T13:30:15Z",
  "quality_flags": []
}
```

Increment the schema version if downstream consumers require strict field sets; otherwise add
backward-compatible optional properties only with their agreement.

## 7. Implementation and validation plan

### Phase 1 — make the zero-deposit route honest

1. Remove the historical-data hard gate; resolve live price independently.
2. Route on data completeness/freshness. If IB is empty, stale, or incomplete, use Finviz and state
   the reason.
3. Promote the working Finviz Elite screener to market-wide candidate discovery.
4. Preserve `ib_shortable_shares` through ranking, GUI/API, and tests.
5. Enforce float below 20 million on every provider path.
6. Replace the IB daily-volume proxy with a valid intraday calculation or Finviz relative volume.

### Phase 1B — implement the required Schwab provider

1. Complete Individual Developer registration and obtain approved Trader API app credentials.
2. Register a localhost callback and implement a manual first-time OAuth authorization flow.
3. Store app credentials and refresh tokens only in `.env`/local state excluded from Git.
4. Implement token refresh with expiry tracking, clear reauthorization status, and no credential
   logging.
5. Implement and test the official quote, price-history, movers, market-hours, instrument lookup,
   and streaming market-data endpoints available to the approved app.
6. Normalize Schwab output into the same candidate/field contract as Finviz and IB, retaining
   `source`, `observed_at`, market-data delay/status, and quality flags.
7. Keep account/trading scopes separated and order submission disabled.
8. Add mocked offline tests plus market-hours contract tests, then document rate limits and token
   renewal based on the signed-in official specification.

### Phase 2 — implement short interest correctly

1. Normalize `shares_short`, `float_shares`, sources, and separate `as_of` values.
2. Add tested pure functions for short-float percentage and days to cover.
3. Add input validation, null reasons, and provider comparison tolerances.
4. Add fields to GUI, schema snapshot, local API, optional cloud mirror, tests, README, advisor
   notes, and integration handoff.
5. Keep daily short-sale volume and IB inventory in separately named optional fields.

### Phase 3 — collect live market-hours evidence

Run on at least three regular U.S. market sessions:

1. Request 20-50 scanner candidates with the current unsubscribed IB account.
2. Record IB market-data type callbacks, timestamps, entitlement errors, and delay per symbol.
3. Confirm Finviz supplies the real-time price/change path when IB is delayed or unavailable.
4. Do not score delayed IB volume as live relative volume.
5. Confirm fallback works when IB connects but cannot produce complete rows.
6. Confirm 15-second delivery without overlapping refresh workers.
7. Verify reported short interest remains stable between reporting cycles while live fields update.

Evidence: timestamped logs, `/health`, sample `/screener`, and a small comparison CSV. No order is
needed.

### Phase 4 — handoff

1. Give operators `.env.example`, never credentials or the real `.env`.
2. State that data access is single-user and credential-dependent; each runtime needs authorization.
3. Document the field-level source/cadence table.
4. Keep sentiment omitted when the downstream replacement is enabled.
5. Treat paid consolidated IB data as an optional advisor decision, not part of this baseline.

## 8. Quote to give the professor

> No $500 deposit is required if the baseline uses the already available Finviz Elite real-time
> screener. The current IB account returns delayed/unentitled API data, and IBKR's API documentation
> says live API quotes and historical bars require paid Level 1 subscriptions. If live data must
> come specifically through IB, the account normally needs $500 equity plus the applicable market-
> data fees. Otherwise, Finviz supplies the live screening fields while IB remains a delayed or
> optional broker integration. Short interest is calculated separately from the latest reported
> shares short and float, with its reporting date preserved.

Do not promise live IB API data from the current account. Promise Finviz-based live screening with
source-labeled IB degradation, or quote the IB funding/subscription requirement explicitly.

## 9. Primary sources

- [IBKR required minimums](https://www.interactivebrokers.com/en/accounts/required-minimums.php)
- [IBKR pricing and included free Cboe One/IEX feed](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)
- [IBKR paid API subscription requirements](https://ibkrcampus.com/campus/ibkr-api-page/market-data-subscriptions/)
- [IBKR paper-account delayed data](https://www.interactivebrokers.com/en/trading/papertrader-delayed-data.php)
- [IBKR API documentation, including tick 236](https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/)
- [Finviz Elite real-time/API features](https://finviz.com/elite)
- [Finviz screener definitions](https://elite.finviz.com/help/screener)
- [FINRA short-interest reporting](https://www.finra.org/filing-reporting/regulatory-filing-systems/short-interest)
- [FINRA Equity Short Interest data](https://www.finra.org/finra-data/browse-catalog/equity-short-interest/data)
- [FINRA glossary and days-to-cover formula](https://www.finra.org/finra-data/browse-catalog/equity-short-interest/glossary)
- [FINRA short interest versus daily short-sale volume](https://www.finra.org/rules-guidance/notices/information-notice-051019)
- [FINRA Developer Center](https://developer.finra.org/docs)
- [NYSE Group semi-monthly short-interest reference](https://www.nyse.com/market-data/reference)
- [yfinance usage disclaimer](https://ranaroussi.github.io/yfinance/)
- [yfinance screener API](https://ranaroussi.github.io/yfinance/reference/api/yfinance.screen.html)
- [Finnhub market-data pricing](https://finnhub.io/pricing-stock-api-market-data)
- [Alpha Vantage documentation](https://www.alphavantage.co/documentation/)

## 10. Remaining live-verification questions

- Which IB scanner and shortable-share fields still populate without paid Level 1 data?
- What exact market-data type/error does each requested API field return?
- May the advisor-provided Finviz authorization be used after handoff?
- Which official/listing-exchange short-interest adapter and license will the receiving runtime use?
- What discrepancy tolerance should trigger a short-float quality flag?
- Does the integration consumer prefer a schema-version increment?

These are validation tasks, not reasons to deposit $500.
