import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import yfinance as yf

from core.sentiment import train_or_load_model, classify_headlines

LABELED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labeled_data.csv")

# Real financial headlines, real subsequent price moves - as opposed to the existing dataset's
# hand-written headlines. yfinance's `.news` is a live/rolling feed (only ~10 recent items per
# ticker, no deep archive), so volume comes from casting a wide net across many tickers rather
# than pulling lots of history from a few. Mixes volatile small/meme caps (this app's actual
# domain) with liquid large caps (higher headline volume, more "clean" earnings-beat/miss moves).
TICKERS = [
    # Volatile small/micro-caps and past meme names - this app's actual domain. Kept a smaller
    # slice of these deliberately: an earlier run found headlines for names mid-huge-rally
    # (RIOT +91%, BB +243%) mostly produce momentum-reversal noise, not headline-driven moves.
    "GME", "AMC", "KOSS", "SOFI", "PLTR", "COIN", "HOOD",
    "CVNA", "UPST", "AFRM", "BB", "NOK",
    "BIIB", "CLOV", "WKHS", "LCID", "RIVN", "FUBO",
    # Large/mega caps - headline volume, and earnings-beat/miss moves tend to track the headline
    # text more cleanly than already-extended momentum names do.
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC",
    "JPM", "BAC", "WFC", "GS", "MS", "XOM", "CVX", "WMT", "TGT", "COST",
    "DIS", "BA", "GE", "F", "GM", "CAT", "DE", "HON", "MMM", "LMT",
    "PFE", "MRNA", "JNJ", "UNH", "CVS", "KO", "PEP", "MCD", "SBUX", "NKE",
    "ORCL", "CRM", "ADBE", "QCOM", "CSCO", "IBM", "TXN", "AVGO", "MU", "HPQ",
    "T", "VZ", "TMUS", "UPS", "FDX", "DAL", "UAL", "LUV", "NEE", "DUK",
    "V", "MA", "PYPL", "AXP", "SCHW", "BLK", "C", "USB", "PNC", "TFC",
    "ABT", "LLY", "BMY", "GILD", "AMGN", "REGN", "VRTX", "ISRG", "MDT", "SYK",
    "HD", "LOW", "TJX", "ROST", "BBY", "M", "KSS", "DKS", "ULTA",
    # Round 2: broader sector coverage not yet touched (semis, REITs/utilities, telecom/staples,
    # industrials, more mid-cap biotech/tech) - more raw candidates for the agreement filter to
    # draw from, without re-querying tickers already exhausted in round 1.
    "ASML", "AMAT", "LRCX", "KLAC", "ADI", "NXPI", "ON", "MRVL", "SWKS", "MPWR",
    "AMT", "PLD", "EQIX", "PSA", "O", "SPG", "DLR", "WELL", "AVB", "EQR",
    "SO", "D", "AEP", "EXC", "XEL", "ED", "PCG", "SRE", "PPL", "FE",
    "PG", "CL", "KMB", "GIS", "K", "HSY", "MDLZ", "STZ", "CLX", "CHD",
    "MMC", "AON", "TRV", "ALL", "PGR", "MET", "PRU", "AIG", "CB", "HIG",
    "MO", "PM", "STE", "BDX", "ZTS", "IDXX", "DXCM", "ALGN", "EW", "HOLX",
    "ETSY", "EBAY", "PINS", "SNAP", "ROKU", "TTD", "DASH", "ABNB", "UBER", "LYFT",
    "SQ", "SHOP", "DOCU", "ZM", "OKTA", "DDOG", "NET", "CRWD", "PANW", "FTNT",
    # Round 3: further sector/volume expansion (energy, materials, more industrials/consumer/
    # financials/healthcare/tech, ADRs, more volatile names) - by now the agreement filter has
    # proven it reliably kills momentum-reversal noise, so no need to hand-pick "calm" tickers.
    "COP", "SLB", "EOG", "OXY", "HAL", "MPC", "PSX", "VLO", "KMI", "WMB",
    "LIN", "APD", "ECL", "NEM", "FCX", "NUE", "DOW", "DD", "ALB", "MOS",
    "RTX", "NOC", "GD", "EMR", "ITW", "PH", "ETN", "ROK", "CMI", "PCAR",
    "MAR", "HLT", "YUM", "CMG", "DPZ", "EXPE", "BKNG", "RCL", "CCL", "NCLH",
    "COF", "DFS", "SYF", "ALLY", "RJF", "STT", "NTRS", "KEY", "RF", "CFG",
    "CI", "HUM", "ELV", "CNC", "MOH", "ABBV", "TMO", "DHR", "WAT", "A",
    "NOW", "INTU", "WDAY", "TEAM", "HUBS", "ZS", "MDB", "SNOW", "TWLO", "ADSK",
    "BABA", "JD", "PDD", "NIO", "XPEV", "TSM", "SONY", "TM", "RIO", "BHP",
    "MARA", "RIOT", "MSTR", "IONQ", "RGTI", "SMCI", "SIRI", "DKNG", "PENN", "WISH",
    "CMCSA", "CHTR", "WBD", "PARA", "FOXA", "LYV", "SPOT", "ANF", "AEO", "CROX",
    "DECK", "SKX", "VFC", "STLA", "FSLR", "ENPH", "RUN", "PLUG", "CHPT", "BLNK",
]

# A headline needs at least this much elapsed time before its "next trading day" close is a
# settled, available data point - not just "today hasn't finished yet."
MIN_HEADLINE_AGE = timedelta(days=2)

# Decisive-move thresholds: only keep clearly-directional or clearly-flat moves, discarding the
# ambiguous middle band (a single headline rarely fully explains a +/-1% day one way or the
# other - keeping only the extremes reduces label noise from unrelated market/company news).
POSITIVE_THRESHOLD = 0.02
NEGATIVE_THRESHOLD = -0.02
NEUTRAL_BAND = 0.003


def _label_history_for_headline(history, headline_date):
    # history is a DataFrame indexed by date (tz-naive, one row per trading day) with a Close col.
    trading_days = history.index
    on_or_before = trading_days[trading_days <= headline_date]
    if len(on_or_before) == 0:
        return None
    day_of = on_or_before[-1]
    after = trading_days[trading_days > day_of]
    if len(after) == 0:
        return None
    next_day = after[0]

    close_of = history.loc[day_of, "Close"]
    close_next = history.loc[next_day, "Close"]
    if close_of == 0:
        return None
    pct_change = (close_next - close_of) / close_of

    if pct_change >= POSITIVE_THRESHOLD:
        return 1, pct_change
    if pct_change <= NEGATIVE_THRESHOLD:
        return -1, pct_change
    if abs(pct_change) <= NEUTRAL_BAND:
        return 0, pct_change
    return None  # ambiguous middle band - discarded, not force-bucketed


# Sources today's biggest gainers/losers as extra candidate tickers, on top of the static
# TICKERS list. Volatile-right-now stocks tend to also have decisive moves scattered through
# their recent headline history (not just today), so this biases the ticker pool toward names
# more likely to clear the decisive-move threshold - a much higher hit rate per API call than
# picking arbitrary calm large caps. Fresh names each run, so this also grows the pool over time
# without needing to keep hand-picking new tickers.
def _get_mover_tickers(count=50):
    movers = set()
    for screen_id in ("day_gainers", "day_losers"):
        try:
            result = yf.screen(screen_id, count=count)
            movers.update(q["symbol"] for q in result.get("quotes", []) if q.get("symbol"))
        except Exception as e:
            print(f"⚠️ Error fetching {screen_id} screener: {e}")
    return sorted(movers)


def collect(tickers=None):
    tickers = tickers if tickers is not None else TICKERS
    existing = pd.read_csv(LABELED_DATA_PATH, encoding="utf-8")
    seen_headlines = set(existing["headline"])

    cutoff = datetime.now(timezone.utc) - MIN_HEADLINE_AGE
    new_rows = []

    for ticker in tickers:
        try:
            news_items = yf.Ticker(ticker).news or []
        except Exception as e:
            print(f"⚠️ Error fetching news for {ticker}: {e}")
            continue

        candidates = []
        for item in news_items:
            content = item.get("content", {}) or {}
            headline = content.get("title")
            pub_date_str = content.get("pubDate")
            if not headline or not pub_date_str or headline in seen_headlines:
                continue
            try:
                pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
            except ValueError:
                continue
            if pub_date > cutoff:
                continue
            candidates.append((headline, pub_date))

        if not candidates:
            continue

        try:
            history = yf.Ticker(ticker).history(period="3mo")
        except Exception as e:
            print(f"⚠️ Error fetching price history for {ticker}: {e}")
            continue
        if history.empty:
            continue
        history.index = history.index.tz_localize(None)

        for headline, pub_date in candidates:
            result = _label_history_for_headline(history, pub_date.replace(tzinfo=None))
            if result is None:
                continue
            label, pct_change = result
            seen_headlines.add(headline)
            new_rows.append({"headline": headline, "price_movement": label})
            print(f"[{ticker:5s} {label:+d} ({pct_change:+.2%})] {headline}")

    return pd.DataFrame(new_rows)


# A raw price move often has nothing to do with the specific headline it's paired with -
# already-extended momentum names in particular tend to reverse for reasons unrelated to any one
# article (mean reversion, broader market moves, unrelated news). Requiring the headline's own
# text sentiment to agree with the price direction keeps only the decisive, unambiguous examples -
# "beats earnings, stock jumps" - and throws out the "positive headline, stock fell anyway (was
# overextended)" contradictions that would otherwise teach the model the wrong thing.
#
# Uses train_or_load_model()'s default (fine-tuned + zero-shot ensemble) as the judge rather than
# a hardcoded zero-shot-only model - it's the most accurate classifier available at the time this
# runs (measured 68.75% vs. zero-shot's 54%, PROJECT_NOTES.md §8f), so it should both recover
# genuinely-fine examples that a weaker judge would wrongly discard and catch bad ones a weaker
# judge would wrongly keep. This does mean later collection rounds lean on the current model's own
# judgment (semi-supervised bootstrapping) rather than a fixed, independent judge - worth knowing
# if label quality ever needs auditing again the way tests/audit_labeled_data.py did initially.
def _filter_by_text_agreement(new_df):
    if new_df.empty:
        return new_df

    model, vectorizer = train_or_load_model()
    result_df = classify_headlines(new_df["headline"].tolist(), model, vectorizer)
    label_to_movement = {"\U0001F4C8 Positive": 1, "\U0001F610 Neutral": 0, "\U0001F4C9 Negative": -1}
    text_labels = [label_to_movement[p] for p in result_df["prediction"]]

    agree_mask = [t == p for t, p in zip(text_labels, new_df["price_movement"])]
    agree = new_df[agree_mask]
    print(f"\nText-sentiment/price-direction agreement filter: kept {len(agree)}/{len(new_df)} "
          f"(discarded {len(new_df) - len(agree)} where the price move likely wasn't about this headline)")
    return agree


def main():
    movers = _get_mover_tickers()
    combined_tickers = sorted(set(TICKERS) | set(movers))
    print(f"Ticker pool: {len(TICKERS)} static + {len(movers)} today's movers "
          f"= {len(combined_tickers)} unique tickers.\n")

    new_df = collect(combined_tickers)
    if new_df.empty:
        print("\nNo new usable headlines found this run.")
        return

    print(f"\nCollected {len(new_df)} candidate real, price-labeled headlines (pre-filter).")
    filtered_df = _filter_by_text_agreement(new_df)
    if filtered_df.empty:
        print("\nNothing survived the agreement filter this run.")
        return
    print(filtered_df["price_movement"].value_counts())

    existing = pd.read_csv(LABELED_DATA_PATH, encoding="utf-8")
    combined = pd.concat([existing, filtered_df[["headline", "price_movement"]]], ignore_index=True)
    combined.to_csv(LABELED_DATA_PATH, index=False, encoding="utf-8")
    print(f"\nAppended to {LABELED_DATA_PATH} - now {len(combined)} total rows.")


if __name__ == "__main__":
    main()
