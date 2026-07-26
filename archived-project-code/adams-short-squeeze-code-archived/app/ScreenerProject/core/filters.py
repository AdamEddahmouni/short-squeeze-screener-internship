from datetime import datetime, timezone

import pandas as pd
from core.finviz_api import fetch_finviz_data

# Converts a percentage string like '12.3%' to float 12.3
def clean_percent(value):
    try:
        return float(value.strip('%'))
    except:
        return None

# Converts a float string like '5.1M' to 5100000
def clean_float(value):
    try:
        return int(value) * 1000000
    except:
        return None

# Calculates percentage change from previous close
def change_from_close(price, prev_close):
    if pd.isna(price) or pd.isna(prev_close) or price == 0:
        return '0'
    change_pct = ((price - prev_close) / prev_close) * 100
    return change_pct

# Computes the target/stop-loss percentages from weekly volatility and RSI(14).
# Shared by the Finviz path (below) and core/ib_api.py, which derives vol_w/rsi
# from IB's own historical bars instead of Finviz's CSV columns.
def compute_target_stop(vol_w, rsi):
    target = round(0.7 * vol_w + 0.03 * (70 - rsi), 2)
    stop = round((0.3 * vol_w - 0.02 * (rsi - 50)) * -1, 2)
    return target, stop

# Applies all filters to Finviz data to identify high-potential stocks
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Previous Close"] = pd.to_numeric(df["Prev Close"], errors="coerce")
    df["Change%"] = df.apply(lambda row: change_from_close(row["Price"], row["Previous Close"]), axis=1)
    df["Rel Volume"] = pd.to_numeric(df["Relative Volume"], errors="coerce")
    df["Float"] = df["Shares Float"].apply(clean_float)

    if "Short Float" in df.columns:
        df["Short Float"] = df["Short Float"].apply(clean_percent)

    filtered_df = df[
        (df["Price"] >= 2) &
        (df["Price"] <= 20) &
        (df["Change%"] >= 10) &
        (df["Rel Volume"] >= 5)
    ]

    if "Short Float" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Short Float"] >= 5]

    return filtered_df.reset_index(drop=True)

# Returns a list of filtered stock dictionaries with relevant info
def get_filtered_stocks():
    try:
        df = fetch_finviz_data()
        df = apply_filters(df)
        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                "Ticker": row.get("Ticker", ""),
                "Price": row.get("Price", ""),
                "Float": row.get("Shares Float", ""),
                "RelVolume": row.get("Relative Volume", ""),
                "ChangePercent": row.get("Change", ""),
                "Headline": None
            })
        return stocks
    except Exception as e:
        print(f"❌ Error loading Finviz screener data: {e}")
        return []

# Returns candidate stocks (Finviz path) as a flat list, ready for controller.py's cross-provider
# squeeze-score/tier classification (core/squeeze_score.py::classify_tier(), 2026-07-17 redesign -
# SQUEEZE_FORMULA_REDESIGN_HANDOFF.md). Previously scored+split into Prime/Subprime here via
# core/scoring.py::score_setup(); that split now happens once, cross-provider, in controller.py
# after the composite squeeze score (incl. TTM Squeeze) is computed. score_setup() itself is
# unchanged and no longer called from this function - its only remaining caller is
# core/schwab_api.py's cross-provider corroboration rescoring.
def rank_and_group_stocks():
    try:
        df = fetch_finviz_data()
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Previous Close"] = pd.to_numeric(df["Prev Close"], errors="coerce")
        df["Change%"] = df.apply(lambda row: change_from_close(row["Price"], row["Previous Close"]), axis=1)
        df["Rel Volume"] = pd.to_numeric(df["Relative Volume"], errors="coerce")
        df["Float"] = df["Shares Float"].apply(clean_float)

        if "Short Float" in df.columns:
            df["Short Float"] = df["Short Float"].apply(clean_percent)
        else:
            df["Short Float"] = 0

        df = df.dropna(subset=["Float"])

        candidates = []
        for _, row in df.iterrows():
            try:
                vol_w = float(str(row.get("Volatility (Week)", 0)).replace('%', ''))
            except:
                vol_w = 0
            try:
                rsi = float(row.get("Relative Strength Index (14)", 50))
            except:
                rsi = 50

            target, stop = compute_target_stop(vol_w, rsi)

            stock_data = {
                "Ticker": row.get("Ticker", ""),
                "Price": row.get("Price", ""),
                "Float": row.get("Shares Float", ""),
                "RelVolume": row.get("Relative Volume", ""),
                "ChangePercent": row.get("Change", ""),
                "ShortFloat": row.get("Short Float", ""),
                "Target": target,
                "StopLoss": stop,
                "Headline": None,
                # Finviz's export supplies Short Float% directly but not the raw shares_short
                # count or an average-volume figure this app currently parses, so the locally
                # calculated short_float_percent/days_to_cover formula (core/short_interest.py)
                # can't run on this path - be explicit about that rather than guessing values.
                "SharesShort": None,
                "DaysToCover": None,
                "ShortInterestAsOf": None,
                "ShortInterestSource": None,
                "FloatAsOf": datetime.now(timezone.utc).isoformat(),
                "FloatSource": "finviz",
                "IbShortableShares": None,
                "IbShortableSharesAsOf": None,
                "SchwabHtbQuantity": None,
                "SchwabHtbRate": None,
                "SchwabIsHardToBorrow": None,
                "SchwabHtbAsOf": None,
                # Finviz's export doesn't carry the daily high/low/close bar history TTM Squeeze
                # needs (core/technical_indicators.py::compute_ttm_squeeze()) - explicit None with
                # a quality flag rather than guessing, same as SharesShort/DaysToCover above.
                "TtmSqueezeOn": None,
                "TtmSqueezeMomentum": None,
                # IB-only field (core/ib_borrow_rate.py) - explicit None, same reasoning as
                # IbShortableShares above.
                "IbBorrowFeeRate": None,
                "IbBorrowRebateRate": None,
                "IbBorrowRateAsOf": None,
                "QualityFlags": [
                    "shares_short_unavailable_finviz_export",
                    "days_to_cover_unavailable_finviz_export",
                    "short_float_percent_provider_supplied",
                    "ttm_squeeze_unavailable_finviz_export",
                ],
            }

            candidates.append(stock_data)

        return candidates
    except Exception as e:
        print(f"❌ Error ranking filtered stocks: {e}")
        return []