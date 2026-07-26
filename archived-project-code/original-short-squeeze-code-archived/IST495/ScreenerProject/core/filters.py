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

# Scores and ranks stocks as Prime or Subprime setups
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

        prime, subprime = [], []
        for _, row in df.iterrows():
            score = 0
            if 2 <= row["Price"] <= 20: score += 1
            if row["Change%"] >= 10: score += 1
            if row["Rel Volume"] >= 5: score += 1
            if row["Short Float"] >= 5: score += 1

            try:
                vol_w = float(str(row.get("Volatility (Week)", 0)).replace('%', ''))
            except:
                vol_w = 0
            try:
                rsi = float(row.get("Relative Strength Index (14)", 50))
            except:
                rsi = 50

            target = round(0.7 * vol_w + 0.03 * (70 - rsi), 2)
            stop = round((0.3 * vol_w - 0.02 * (rsi - 50)) * -1, 2)

            stock_data = {
                "Ticker": row.get("Ticker", ""),
                "Price": row.get("Price", ""),
                "Float": row.get("Shares Float", ""),
                "RelVolume": row.get("Relative Volume", ""),
                "ChangePercent": row.get("Change", ""),
                "ShortFloat": row.get("Short Float", ""),
                "Target": target,
                "StopLoss": stop,
                "Headline": None
            }

            if score == 4:
                prime.append(stock_data)
            elif score == 3:
                subprime.append(stock_data)

        return prime, subprime
    except Exception as e:
        print(f"❌ Error ranking filtered stocks: {e}")
        return [], []