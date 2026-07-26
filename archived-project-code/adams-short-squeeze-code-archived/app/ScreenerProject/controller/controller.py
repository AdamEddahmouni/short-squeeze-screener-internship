import csv
import re
import sys
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

from datetime import datetime, timezone
try:
    from playsound import playsound
except ImportError:
    playsound = None  # Audio backend not installed/available - alert becomes a silent no-op.
try:
    from core.sentiment import train_or_load_model, classify_headlines
except ImportError as sentiment_import_error:
    train_or_load_model = None
    classify_headlines = None
    SENTIMENT_IMPORT_ERROR = sentiment_import_error
else:
    SENTIMENT_IMPORT_ERROR = None
from core.finviz_api import fetch_all_finviz_api_news, FINVIZ_API_KEY
from core.yfinance_news_api import fetch_yfinance_news
from core.newsapi_news_api import fetch_newsapi_news, NEWSAPI_KEY
import webbrowser
from core.filters import rank_and_group_stocks
from core.snapshot_store import SCHEMA_VERSION
import core.ib_api as ib_api
import core.schwab_api as schwab_api
from core.squeeze_score import (
    compute_squeeze_score,
    compute_squeeze_score_breakdown,
    classify_tier,
    is_squeeze_confirmed,
    is_ttm_squeeze_fired,
)
from core import squeeze_score_history, corroboration_history

# Temporary stand-in for real discovery (blocked pending the IB scanner work,
# PROJECT_NOTES.md §8) so the Breaking News tab isn't always empty in the
# meantime. Superseded automatically once discovery returns real tickers.
DEFAULT_WATCHLIST = ["GME", "AMC", "KOSS", "PLTR", "SOFI"]

PRIME_ALERT_SOUND = os.path.join(BASE_DIR, "assets", "prime_alert.mp3")

# Discovery-source order: first available wins each cycle. Configurable per deployment/operator
# via SCREENER_PROVIDER_PRIORITY (comma-separated, e.g. "schwab,ib") in .env - lets the
# integration team pick/reorder/drop providers without touching code. Finviz has no real
# availability gate of its own (fetch_finviz_data() degrades to an empty result without a key,
# PROJECT_NOTES.md §6) so it's always eligible as the last-resort entry, same as before this
# dispatch existed.
DEFAULT_PROVIDER_PRIORITY = ["ib", "schwab", "finviz"]


class Controller:

    # Logs a prime ticker to the prime_log.csv file if not already logged today. Returns True if
    # this was a genuinely new entry (vs. a same-day duplicate) - callers use this to decide
    # whether/how to alert, rather than this function playing a sound itself for every single
    # ticker (a scan cycle can surface many new Prime tickers at once - see get_screener_results()).
    def log_prime_ticker(ticker_data):
        log_path = os.path.join(BASE_DIR, "data", "prime_log.csv")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        fields = ["timestamp", "ticker", "price", "target", "stop_loss", "sentiment"]
        new_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticker": ticker_data.get("Ticker"),
            "price": ticker_data.get("Price"),
            "target": ticker_data.get("Target"),
            "stop_loss": ticker_data.get("StopLoss"),
            "sentiment": ticker_data.get("Sentiment", "")
        }

        # Avoid duplicates. Tolerates a malformed/short row (missing/unparseable timestamp) by
        # skipping just that row rather than raising - caught live 2026-07-16: a stray blank line
        # ahead of the real header (introduced by a merge that reintroduced an old empty version
        # of this file) made every row parse under the wrong field names, and the resulting
        # KeyError propagated out of this Tkinter-scheduled callback uncaught, permanently killing
        # the screener's refresh timer chain (root.after() never got to reschedule itself) - the
        # window kept responding to input, but the snapshot silently froze forever. A malformed
        # log file should never be able to take down live scoring.
        if os.path.exists(log_path):
            with open(log_path, "r", newline="", encoding="utf-8") as f:
                today = datetime.now(timezone.utc).date()

                for row in csv.DictReader(f):
                    try:
                        row_date = datetime.fromisoformat(row["timestamp"]).date()
                    except (KeyError, TypeError, ValueError):
                        continue

                    if row["ticker"] == new_entry["ticker"] and row_date == today:
                        return False  # Already logged today

        with open(log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)

            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(new_entry)

        return True

    # Plays the Prime-setup alert chime once, non-blocking (playsound's default blocks the
    # calling thread for the sound's full duration - on the Tkinter main thread, that would freeze
    # the UI for as long as the sound plays). Best-effort: a missing/broken audio backend on some
    # machine shouldn't take down the screener loop.
    @staticmethod
    def _play_prime_alert():
        if playsound is None:
            return
        try:
            playsound(PRIME_ALERT_SOUND, block=False)
        except Exception as e:
            print(f"⚠️ Error playing Prime-setup alert sound: {e}")

    # Loads the sentiment model, starts the (non-blocking) IB scanner connection,
    # and fetches an initial batch of news headlines
    def __init__(self):
        if train_or_load_model is None:
            print(f"Sentiment dependencies unavailable; continuing without sentiment: {SENTIMENT_IMPORT_ERROR}")
            self.model, self.vectorizer = None, None
        else:
            self.model, self.vectorizer = train_or_load_model()
        ib_api.start_ib_connection()

        # Cheap startup diagnostic so Schwab's setup state (not_configured/not_yet_authorized/
        # needs_reauth/ready - core/schwab_api.py's health()) is visible without a separate
        # health check; a still-blank .env or an expired 7-day refresh token isn't a bug, just
        # not fully wired up yet.
        schwab_status = schwab_api.health()
        if schwab_status["status"] != "ready":
            print(f"Schwab Trader API not active yet ({schwab_status['status']}): {schwab_status.get('detail')}")

        self._current_source = "finviz"  # updated every cycle by get_screener_results()
        # Cross-cycle TTM Squeeze state (2026-07-17, "fired" detection) - {ticker: last-seen
        # squeeze_on bool}, plus which provider produced it. See _apply_ttm_fired() for why the
        # source is tracked alongside the state instead of trusting it across a provider switch.
        self._ttm_state = {}
        self._ttm_state_source = None
        # Overwritten with real discovered tickers on the first get_screener_results() cycle;
        # only the placeholder watchlist until then (startup, or if discovery never returns
        # anything this run) - see get_positive_news() for why this needs to be remembered here.
        self._last_watchlist = DEFAULT_WATCHLIST
        self.refresh_news_cache(DEFAULT_WATCHLIST)

    # Every entry: (source_name, is_available_fn, rank_and_group_fn). Finviz has no real
    # availability gate of its own so it's always eligible - see DEFAULT_PROVIDER_PRIORITY above.
    @staticmethod
    def _provider_table():
        return {
            "ib": ("ib", ib_api.is_ib_available, ib_api.rank_and_group_stocks_ib),
            "schwab": ("schwab", schwab_api.is_available, schwab_api.rank_and_group_stocks_schwab),
            "finviz": ("finviz", lambda: True, rank_and_group_stocks),
        }

    # Discovery-source order from SCREENER_PROVIDER_PRIORITY (see DEFAULT_PROVIDER_PRIORITY above
    # for the fallback and rationale).
    @staticmethod
    def _provider_priority():
        raw = os.environ.get("SCREENER_PROVIDER_PRIORITY", "")
        order = [name.strip().lower() for name in raw.split(",") if name.strip()]
        return order or DEFAULT_PROVIDER_PRIORITY

    # Picks the first available provider in priority order. An available-but-empty cycle (e.g.
    # IB connected with zero matching stocks) is still a valid result, not a fallback trigger -
    # only a genuinely unavailable provider is skipped.
    def _select_provider(self):
        table = self._provider_table()
        for name in self._provider_priority():
            entry = table.get(name)
            if entry and entry[1]():
                return entry
        return table["finviz"]

    # Gracefully stops the IB connection/thread - call on app shutdown.
    @staticmethod
    def shutdown_ib():
        ib_api.stop_ib_connection()

    # True if a real Finviz key is configured, opportunistically preferring it
    # over the free yfinance fallback (PROJECT_NOTES.md §8a decision).
    @staticmethod
    def _should_use_finviz():
        return bool(FINVIZ_API_KEY)

    # True if a NewsAPI key is configured via the NEWSAPI_KEY env var - last-resort
    # third tier, only consulted when yfinance itself returns nothing (§8b).
    @staticmethod
    def _should_use_newsapi():
        return bool(NEWSAPI_KEY)

    # Picks which tickers to fetch news for: the discovered prime/subprime
    # tickers if any, else the placeholder watchlist above.
    @staticmethod
    def _get_watchlist_tickers(prime, subprime):
        tickers = sorted({s.get("Ticker") for s in prime + subprime if s.get("Ticker")})
        return tickers or DEFAULT_WATCHLIST

    # Re-fetches breaking news so headline/sentiment matching stays current. Tries Finviz's bulk
    # export first if a real key is configured, but a configured key is not the same as a working
    # one (caught live 2026-07-13: an expired key returns 401 and fetch_all_finviz_api_news()
    # swallows that into an empty list) - any empty result, whether from a missing key, a dead
    # key, or a rate limit, falls through to per-ticker yfinance news, then further to NewsAPI only
    # if yfinance also comes back empty. NewsAPI is last since its free tier is quota-capped and
    # more stale than yfinance.
    def refresh_news_cache(self, tickers=None):
        watchlist = tickers or DEFAULT_WATCHLIST

        news = fetch_all_finviz_api_news() if self._should_use_finviz() else []
        if not news:
            news = fetch_yfinance_news(watchlist)
        if not news and self._should_use_newsapi():
            news = fetch_newsapi_news(watchlist)

        self.news_cache = news

    # Cross-provider corroboration (PROJECT_NOTES.md, CROSS_PROVIDER_CORROBORATION_PLAN.md): the
    # advisor treats agreement between IB and Schwab as a trust signal, not a filter - so this only
    # ever adds metadata to IB's rows, never drops or blocks one. Only attempted when IB is this
    # cycle's winning provider (Finviz is explicitly excluded) and Schwab is independently
    # available; otherwise every row simply gets CorroborationScore=None/CorroboratedBy=[] rather
    # than a faked/misleading value.
    def _apply_corroboration(self, source_name, candidates):
        corroboration = {}
        if source_name == "ib" and schwab_api.is_available():
            tickers = [stock.get("Ticker") for stock in candidates if stock.get("Ticker")]
            corroboration = schwab_api.score_tickers_for_corroboration(tickers)

        for stock in candidates:
            result = corroboration.get(stock.get("Ticker"))
            score = result.get("score") if result else None
            stock["CorroborationScore"] = score
            stock["CorroboratedBy"] = ["schwab"] if score is not None and score >= 3 else []
            # Schwab's hard-to-borrow signal for this ticker, found live 2026-07-16: it was
            # already being fetched/computed as part of scoring above but discarded, so it never
            # reached IB-sourced rows even when corroboration ran. Only overwrites the IB row's
            # None placeholders when Schwab actually had data for this specific ticker.
            if result:
                stock["SchwabHtbQuantity"] = result["schwab_htb_quantity"]
                stock["SchwabHtbRate"] = result["schwab_htb_rate"]
                stock["SchwabIsHardToBorrow"] = result["schwab_is_hard_to_borrow"]
                stock["SchwabHtbAsOf"] = result["schwab_htb_as_of"]

    # Composite squeeze-pressure score (core/squeeze_score.py, advisor request 2026-07-16:
    # "which one is primed to go for a short squeeze"; extended 2026-07-17 with TTM Squeeze as a
    # 4th component, SQUEEZE_FORMULA_REDESIGN_HANDOFF.md) - combines whichever of
    # short_float_percent/ib_borrow_fee_rate/days_to_cover/ttm_squeeze this row actually has.
    # Cross-provider (works the same regardless of which provider sourced the row) so it lives
    # here rather than being duplicated in each provider module, same reasoning as
    # _apply_corroboration() above. This score is now also the input to Prime/Subprime tier
    # classification (see _split_by_tier()), not just a display-only ranking aid.
    @staticmethod
    def _apply_squeeze_score(candidates):
        for stock in candidates:
            short_float = Controller._to_number(stock.get("ShortFloat"))
            borrow_fee = stock.get("IbBorrowFeeRate")
            days_to_cover = stock.get("DaysToCover")
            ttm_squeeze_on = stock.get("TtmSqueezeOn")
            ttm_squeeze_momentum = stock.get("TtmSqueezeMomentum")
            stock["SqueezeScore"] = compute_squeeze_score(
                short_float, borrow_fee, days_to_cover, ttm_squeeze_on, ttm_squeeze_momentum
            )
            # Additive: the four per-component sub-scores behind the composite above, so the web
            # UI's detail panel can show which factor is actually driving a ticker's score instead
            # of just the final number.
            stock["SqueezeScoreBreakdown"] = compute_squeeze_score_breakdown(
                short_float, borrow_fee, days_to_cover, ttm_squeeze_on, ttm_squeeze_momentum
            )

    # Independent "is this actively squeezing right now" flag (core/squeeze_score.py::
    # is_squeeze_confirmed(), 2026-07-17 redesign) - separate from Prime/Subprime tier, direct
    # answer to the advisor's "we don't want to open them one by one."
    @staticmethod
    def _apply_squeeze_confirmed(candidates):
        for stock in candidates:
            rel_volume = Controller._to_number(stock.get("RelVolume"))
            change_percent = Controller._to_number(stock.get("ChangePercent"))
            stock["SqueezeConfirmed"] = is_squeeze_confirmed(
                rel_volume, change_percent, stock.get("TtmSqueezeMomentum")
            )

    # Cross-cycle "did TTM compression just release" detection (2026-07-17) - a leading
    # counterpart to _apply_squeeze_confirmed()'s lagging (already-moved-50%) signal, answering
    # the same advisor complaint ("catch it before it jumps") from the other side. Not static:
    # needs self._ttm_state, the first in-memory cross-cycle per-ticker state this codebase has
    # needed - see core/squeeze_score.py::is_ttm_squeeze_fired() for the actual transition logic.
    def _apply_ttm_fired(self, source_name, candidates):
        # Provider switched since state was last recorded -> the old state came from a
        # different bar fetch entirely (IB vs Schwab each cache their own 30-day bars
        # independently), not a real transition - discard it rather than risk a false fire.
        # getattr, not self._ttm_state directly: production always goes through __init__, but
        # tests construct via Controller.__new__() and skip it (same reason get_snapshot() reads
        # self._current_source via getattr above).
        prior_source = getattr(self, "_ttm_state_source", None)
        prior_state = getattr(self, "_ttm_state", {}) if source_name == prior_source else {}
        next_state = {}
        for stock in candidates:
            ticker = stock.get("Ticker")
            current_on = stock.get("TtmSqueezeOn")
            stock["TtmSqueezeFired"] = is_ttm_squeeze_fired(
                prior_state.get(ticker), current_on, stock.get("TtmSqueezeMomentum")
            )
            if ticker:
                # Preserve the last known boolean across a transient None reading (e.g. a
                # one-cycle ttm_squeeze_unavailable gap, ib_api.py's "fewer than 21 daily bars"
                # case) instead of wiping memory of a real prior compression state. Safe: only
                # is_ttm_squeeze_fired()'s own strict prev-is-True/current-is-False check can
                # ever produce True, so this can't fabricate a signal, only avoid losing one.
                next_state[ticker] = current_on if current_on is not None else prior_state.get(ticker)
        self._ttm_state = next_state
        self._ttm_state_source = source_name

    # Quality flags (2026-07-17 redesign) - observational metadata, never a scoring input.
    # Extends whatever a provider already put in QualityFlags (e.g. core/filters.py's Finviz-path
    # "data unavailable" flags) rather than overwriting it. Runs after tier is known (prime/
    # subprime already split) and after sentiment_for() is available (built from this cycle's
    # matched headlines) - see get_screener_results() for the ordering this depends on.
    # - sentiment_mismatch: tier is Prime but sentiment reads Neutral/Negative (the advisor's KLRS
    #   complaint - "your expectation is KLRS is prime, but sentiment is neutral").
    # - borrow_fee_feed_down: every IB-sourced candidate this cycle is missing ib_borrow_fee_rate,
    #   distinguishing a systemic feed outage (SQUEEZE_FORMULA_REDESIGN_HANDOFF.md §2 - the IB FTP
    #   borrow-rate feed was confirmed unreachable at the TCP level one session) from a single
    #   ticker just happening to lack the field.
    @staticmethod
    def _apply_quality_flags(source_name, prime, subprime, sentiment_for):
        candidates = prime + subprime
        borrow_fee_feed_down = (
            source_name == "ib"
            and bool(candidates)
            and all(stock.get("IbBorrowFeeRate") is None for stock in candidates)
        )
        for stock in prime:
            match = Controller._SENTIMENT_RE.search(sentiment_for(stock.get("Ticker", "")) or "")
            if match and match.group(1) in ("Neutral", "Negative"):
                stock["QualityFlags"] = list(stock.get("QualityFlags") or []) + ["sentiment_mismatch"]
        if borrow_fee_feed_down:
            for stock in candidates:
                stock["QualityFlags"] = list(stock.get("QualityFlags") or []) + ["borrow_fee_feed_down"]

    # Prime/Subprime split (2026-07-17 redesign) off the composite squeeze score rather than
    # core/scoring.py::score_setup() - see core/squeeze_score.py::classify_tier(). A None tier
    # (missing score, or score below the Subprime floor) drops the row entirely, same as
    # score_setup() scoring below 3 used to.
    @staticmethod
    def _split_by_tier(candidates):
        prime, subprime = [], []
        for stock in candidates:
            short_float = Controller._to_number(stock.get("ShortFloat"))
            tier = classify_tier(stock.get("SqueezeScore"), short_float)
            if tier == "prime":
                prime.append(stock)
            elif tier == "subprime":
                subprime.append(stock)
        return prime, subprime

    # Generates formatted screener results for Prime and Subprime setups with sentiment
    def get_screener_results(self):
        source_name, _is_available, rank_fn = self._select_provider()
        self._current_source = source_name
        candidates = rank_fn()
        self._apply_corroboration(source_name, candidates)
        self._apply_squeeze_score(candidates)
        self._apply_squeeze_confirmed(candidates)
        self._apply_ttm_fired(source_name, candidates)
        # Tier classification (2026-07-17 redesign) off the composite squeeze score - see
        # _split_by_tier(). Replaces the old per-provider score_setup()-based split.
        prime, subprime = self._split_by_tier(candidates)
        squeeze_score_history.append_scores(
            (stock.get("Ticker"), stock.get("SqueezeScore")) for stock in prime + subprime
        )
        corroboration_history.append_scores(
            (stock.get("Ticker"), stock.get("CorroborationScore")) for stock in prime + subprime
        )
        # Remembered for get_positive_news()'s own independent timer chain (see there for why) -
        # this is the one place real discovered tickers are known this cycle.
        self._last_watchlist = self._get_watchlist_tickers(prime, subprime)
        self.refresh_news_cache(self._last_watchlist)

        def matched_headline(ticker):
            for news in self.news_cache:
                if ticker in news.get("tickers", []):
                    return news.get("headline", "")
            return ""

        all_stocks = prime + subprime
        headline_by_ticker = {
            stock.get('Ticker', ''): matched_headline(stock.get('Ticker', '')) for stock in all_stocks
        }

        # Found live 2026-07-14: this used to call classify_headlines() once per ticker (and, for
        # Prime tickers, a second time again in the loop below) - each call is its own FinBERT
        # forward pass on the Tkinter main thread, so a cycle with several tickers ran the model
        # N (or 2N) times sequentially and was the likely cause of the window periodically going
        # unresponsive mid-refresh. One batched call across every distinct headline this cycle
        # actually needs is both correct (transformer inference batches far more efficiently than
        # N single-item calls) and eliminates the Prime double-classification outright.
        sentiment_by_headline = {}
        if self.model:
            distinct_headlines = sorted({h for h in headline_by_ticker.values() if h})
            if distinct_headlines:
                df = classify_headlines(distinct_headlines, self.model, self.vectorizer)
                for _, row in df.iterrows():
                    sentiment_by_headline[row['headline']] = (
                        f"{row['prediction']} ({int(row['confidence_score']*100)}%)"
                    )

        def sentiment_for(ticker):
            headline = headline_by_ticker.get(ticker, "")
            return sentiment_by_headline.get(headline, "") if headline else ""

        self._apply_quality_flags(source_name, prime, subprime, sentiment_for)

        def classify_batch(batch):
            formatted = []
            for stock in batch:
                ticker = stock.get('Ticker', '')
                formatted.append([
                    ticker,
                    stock.get("Price", "?"),
                    stock.get("Float", "?"),
                    stock.get("RelVolume", "?"),
                    stock.get("ChangePercent", "?"),
                    stock.get("Target", "?"),
                    stock.get("StopLoss", "?"),
                    sentiment_for(ticker),
                    stock.get("ShortFloat", "?"),
                    stock.get("SharesShort"),
                    stock.get("DaysToCover"),
                    stock.get("ShortInterestAsOf"),
                    stock.get("ShortInterestSource"),
                    stock.get("FloatAsOf"),
                    stock.get("FloatSource"),
                    stock.get("IbShortableShares"),
                    stock.get("IbShortableSharesAsOf"),
                    stock.get("SchwabHtbQuantity"),
                    stock.get("SchwabHtbRate"),
                    stock.get("SchwabIsHardToBorrow"),
                    stock.get("SchwabHtbAsOf"),
                    stock.get("TtmSqueezeOn"),
                    stock.get("TtmSqueezeMomentum"),
                    stock.get("IbBorrowFeeRate"),
                    stock.get("IbBorrowRebateRate"),
                    stock.get("IbBorrowRateAsOf"),
                    stock.get("SqueezeScore"),
                    stock.get("SqueezeScoreBreakdown"),
                    stock.get("CorroborationScore"),
                    stock.get("CorroboratedBy", []),
                    stock.get("QualityFlags", []),
                    stock.get("SqueezeConfirmed", False),
                    stock.get("TtmSqueezeFired", False),
                ])

            return formatted

        any_new_prime = False
        for stock in prime:
            stock["Sentiment"] = sentiment_for(stock.get('Ticker', ''))
            if Controller.log_prime_ticker(stock):
                any_new_prime = True

        # One alert per refresh cycle, not one per new ticker - a single scan can surface several
        # new Prime setups at once (e.g. the first cycle after IB reconnects), and per-ticker
        # alerts would mean playing the same chime back-to-back several times in a row.
        if any_new_prime:
            self._play_prime_alert()

        prime_results = classify_batch(prime)
        subprime_results = classify_batch(subprime)
        return prime_results, subprime_results

    _SENTIMENT_RE = re.compile(r"(Positive|Neutral|Negative)\s*\((\d+)%\)")

    # Sentiment is useful in this app's UI, but it is an optional integration concern because the
    # downstream team is building its own replaceable sentiment component. Keeping the switch at
    # the snapshot boundary means disabling our output does not disturb screening or the desktop UI.
    @staticmethod
    def _include_sentiment_output():
        value = os.environ.get("INCLUDE_SENTIMENT_OUTPUT", "true").strip().lower()
        return value not in {"0", "false", "no", "off"}

    # Coerces a display-formatted field ("?" placeholder, or a real number) into a JSON-friendly
    # float or None - the integration contract (PROJECT_NOTES.md §9) wants typed nulls for
    # missing data, not the "?"/"N/A" placeholder strings the Treeview display uses.
    @staticmethod
    def _to_number(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # Maps get_screener_results()'s already-computed display rows into the integration data
    # contract (PROJECT_NOTES.md §9) - pure post-processing of data the caller already fetched
    # this cycle, not a second computation/poll. Takes prime_results/subprime_results directly
    # (the same two lists get_screener_results() just returned) rather than recomputing them.
    def get_snapshot(self, prime_results, subprime_results):
        # Set by get_screener_results() this same cycle - reused rather than re-selected so the
        # snapshot always reflects whichever provider actually produced prime_results/subprime_results.
        source = getattr(self, "_current_source", "finviz")
        # UTC, matching every other *_as_of provenance field in this same payload (short_interest_as_of,
        # float_as_of, ib_borrow_rate_as_of, schwab_htb_as_of) and /health's last_updated - a prior
        # local-time-with-offset value here looked like a multi-hour discrepancy against those UTC
        # fields when compared side by side (flagged by the advisor as confusing).
        generated_at = datetime.now(timezone.utc).isoformat()

        def to_contract(rows, tier):
            entries = []
            for row in rows:
                (ticker, price, float_shares, rel_volume, change_percent, target, stop_loss,
                 sentiment, short_float, shares_short, days_to_cover, short_interest_as_of,
                 short_interest_source, float_as_of, float_source, ib_shortable_shares,
                 ib_shortable_shares_as_of, schwab_htb_quantity, schwab_htb_rate,
                 schwab_is_hard_to_borrow, schwab_htb_as_of, ttm_squeeze_on, ttm_squeeze_momentum,
                 ib_borrow_fee_rate, ib_borrow_rebate_rate, ib_borrow_rate_as_of, squeeze_score,
                 squeeze_score_breakdown, corroboration_score, corroborated_by, quality_flags,
                 squeeze_confirmed, ttm_squeeze_fired) = row
                entry = {
                    "schema_version": SCHEMA_VERSION,
                    "ticker": ticker,
                    "price": self._to_number(price),
                    "float_shares": self._to_number(float_shares),
                    "rel_volume": self._to_number(rel_volume),
                    "change_percent": self._to_number(change_percent),
                    "short_float_percent": self._to_number(short_float),
                    "target_percent": self._to_number(target),
                    "stop_loss_percent": self._to_number(stop_loss),
                    "setup_tier": tier,
                    "source": source,
                    "timestamp": generated_at,
                    # Short-interest provenance (FRESH_START_DATA_AND_SHORT_INTEREST_PLAN.md §6):
                    # shares_short/short_interest_* describe the officially reported open short
                    # position; ib_shortable_shares is a separate broker-inventory signal and must
                    # never be substituted for it.
                    "shares_short": shares_short,
                    "days_to_cover": days_to_cover,
                    "short_interest_as_of": short_interest_as_of,
                    "short_interest_source": short_interest_source,
                    "float_as_of": float_as_of,
                    "float_source": float_source,
                    "ib_shortable_shares": ib_shortable_shares,
                    "ib_shortable_shares_as_of": ib_shortable_shares_as_of,
                    # Schwab's own borrow-availability signal (found live 2026-07-13, /quotes'
                    # reference.htbQuantity/htbRate/isHardToBorrow) - same "broker inventory, not
                    # official short interest" caveat as ib_shortable_shares above, kept under its
                    # own schwab_htb_* name since it's a different provider's figure.
                    "schwab_htb_quantity": schwab_htb_quantity,
                    "schwab_htb_rate": schwab_htb_rate,
                    "schwab_is_hard_to_borrow": schwab_is_hard_to_borrow,
                    "schwab_htb_as_of": schwab_htb_as_of,
                    # TTM Squeeze (core/technical_indicators.py::compute_ttm_squeeze()) - a
                    # volatility-compression signal (Bollinger Bands inside Keltner Channels),
                    # computed from the same daily bars already fetched for RSI/weekly-volatility.
                    # Feeds into squeeze_score/setup_tier as of the 2026-07-17 redesign (see
                    # core/squeeze_score.py) - no longer purely display-only.
                    "ttm_squeeze_on": ttm_squeeze_on,
                    "ttm_squeeze_momentum": ttm_squeeze_momentum,
                    # IB's own indicative stock-loan borrow cost (core/ib_borrow_rate.py) - a
                    # live-updating (hourly, every 15min 4-6pm ET per IB's own FTP feed cadence)
                    # proxy for squeeze pressure requested by the advisor 2026-07-16: a rising
                    # ib_borrow_fee_rate signals rising demand to borrow/short the stock, unlike
                    # shares_short above which only updates twice a month. IB-only - None on
                    # Schwab/Finviz-sourced rows, never fabricated.
                    "ib_borrow_fee_rate": ib_borrow_fee_rate,
                    "ib_borrow_rebate_rate": ib_borrow_rebate_rate,
                    "ib_borrow_rate_as_of": ib_borrow_rate_as_of,
                    # Composite squeeze-pressure score (core/squeeze_score.py) - combines whichever
                    # of short_float_percent/ib_borrow_fee_rate/days_to_cover/ttm_squeeze this row
                    # has into a single 0-100 number, simplified from Tapeboard's published Short
                    # Squeeze Score methodology (plus TTM Squeeze, this app's own addition). As of
                    # the 2026-07-17 redesign this score (via classify_tier(),
                    # core/squeeze_score.py) is what setup_tier is actually derived from -
                    # core/scoring.py::score_setup() is no longer the classification gate.
                    "squeeze_score": squeeze_score,
                    # The four per-component sub-scores (each 0-100 or None) behind squeeze_score
                    # above - additive, lets a consumer see which factor is actually driving a
                    # ticker's score instead of just the final composite number.
                    "squeeze_score_breakdown": squeeze_score_breakdown,
                    # Cross-provider corroboration (CROSS_PROVIDER_CORROBORATION_PLAN.md §3): only
                    # populated when IB won this cycle and Schwab was independently available -
                    # None/[] otherwise, never a fabricated value. A label, not a filter: rows are
                    # never dropped for lacking corroboration.
                    "corroboration_score": corroboration_score,
                    "corroborated_by": corroborated_by if corroborated_by is not None else [],
                    "quality_flags": quality_flags if quality_flags is not None else [],
                    # Independent "is this actively squeezing right now" flag
                    # (core/squeeze_score.py::is_squeeze_confirmed(), 2026-07-17 redesign) -
                    # separate from setup_tier, the direct answer to the advisor's "we don't want
                    # to open them one by one."
                    "squeeze_confirmed": bool(squeeze_confirmed),
                    # Leading counterpart to squeeze_confirmed above (core/squeeze_score.py::
                    # is_ttm_squeeze_fired(), 2026-07-17): true exactly on the cycle TTM
                    # compression released for this ticker, vs. squeeze_confirmed's lagging
                    # already-moved-50% signal. Real time-resolution is ~1hr (the underlying daily
                    # bars are cached that long per symbol), not sub-minute - see
                    # Controller._apply_ttm_fired().
                    "ttm_squeeze_fired": bool(ttm_squeeze_fired),
                }
                if self._include_sentiment_output():
                    match = self._SENTIMENT_RE.search(sentiment or "")
                    entry.update({
                        "sentiment_label": match.group(1) if match else None,
                        "sentiment_confidence": int(match.group(2)) / 100 if match else None,
                    })
                entries.append(entry)
            return entries

        return to_contract(prime_results, "prime") + to_contract(subprime_results, "subprime")

    """# Classifies a single custom headline
    def classify_single_headline(self, headline):
        if not self.model:
            return None
        
        df = classify_headlines([headline], self.model, self.vectorizer)
        return df.iloc[0] if not df.empty else None"""

    # Returns a list of high-confidence positive headlines from the cached news
    def get_positive_news(self):
        if not self.model:
            return []

        # Bug found live 2026-07-14: this unconditionally fetched news for DEFAULT_WATCHLIST
        # (GME/AMC/KOSS/PLTR/SOFI) forever, never the tickers discovery actually found - the
        # comment on DEFAULT_WATCHLIST above says it's "superseded automatically once discovery
        # returns real tickers," but this method never looked at real tickers at all, so the
        # Breaking News tab stayed pinned to 5 fixed symbols regardless of what the screener
        # found, and looked "stuck" once those 5 ran out of fresh headlines. get_screener_results()
        # runs on its own independent 15s timer chain and is the only place real tickers are known
        # each cycle, so self._last_watchlist (set there) is reused here instead.
        self.refresh_news_cache(self._last_watchlist)
        news = self.news_cache
        headlines = [item['headline'] for item in news]
        df = classify_headlines(headlines, self.model, self.vectorizer)
        positive = []
        for i, row in df.iterrows():
            if "Positive" in row['prediction'] and row['confidence_score'] >= 0.6:
                positive.append({
                    "headline": row['headline'],
                    "confidence_score": row['confidence_score'],
                    "tickers": news[i].get("tickers", []),
                    "url": news[i].get("url", "")
                })
                
        return positive

    # Opens a URL in the default web browser
    def open_url(self, url):
        webbrowser.open_new_tab(url)
