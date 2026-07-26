import requests
import pandas as pd
from datetime import datetime
import os
import io

# 🔑 Your Finviz Elite auth token
FINVIZ_API_KEY = "YOUR API TOKEN HERE"  # dead key archived: archive/legacy-data/deprecated_api_keys.md

# ✅ Tickers you care about
tickers_to_track = ['ACDC', 'AIFF','AIRS', 'ALBT', 'ALGS', 'AMIX', 'ANVS', 'ASTI', 'BBGI', 'BALY', 'BNGO', 'BKKT', 'BTM', 'CYN', 'CLIK', 'CISS', 'RRGB', 'BETR', 'BODI', 'BNZI', 'BOLT', 'BTCT', 'CNSP', 'CNET', 'CVRX', 'DSP', 'DSS', 'DTIL', 'DUO', 'ECOR', 'ELAB', 'EZGO', 'FC', 'FLGT', 'FVR', 'GAMB', 'GWH', 'HCAI', 'HUSA', 'HYPD', 'IBIO', 'ICON', 'INDO', 'INTZ', 'JILL', 'KIRK', 'KYTX', 'LE', 'LIDR', 'LYRA', 'MFH', 'MSGM', 'MMA', 'NAAS', 'NWTG', 'OFAL', 'MVO', 'PTIX', 'QMCO', 'RELI',  'SISI', 'SKYE', 'SLRX', 'SOAR', 'STAK', 'SST', 'TRAK', 'TPET', 'USEA', 'VCIG', 'VEEE', 'WHLR', 'WLGS', 'WOK', 'WXM', 'XELB', 'XXII', 'YAAS', 'YIBO', 'ZUMZ', 'ZYBT', 'ZYXI']

# ✅ Screener export URL (NO stray quotes!)
url = f'https://elite.finviz.com/export.ashx?v=150&c=1,25,26,30,31,84,42,43,49,50,52,53,55,56,57,59,60,61,64,81,86,87&auth={FINVIZ_API_KEY}'

# ✅ Make request
response = requests.get(url)
response.raise_for_status()

# ✅ Read CSV export
df = pd.read_csv(io.StringIO(response.text))

print("\n✅ Screener Columns:", df.columns.tolist())
print(df.head())

# ✅ Filter for tickers you care about
df = df[df['Ticker'].isin(tickers_to_track)]

# ✅ Add Date column
df['Date'] = datetime.now().strftime('%Y-%m-%d')

# ✅ Squeeze check helper function
def classify_squeeze(open_price, high_price):
    if pd.isna(open_price) or pd.isna(high_price) or open_price == 0:
        return 'N'
    gain_pct = ((high_price - open_price) / open_price) * 100
    if gain_pct < 15:
        return 'N'
    elif gain_pct < 30:
        return f'S - {gain_pct:.1f}%'
    elif gain_pct < 60:
        return f'M - {gain_pct:.1f}%'
    elif gain_pct <= 100:
        return f'L - {gain_pct:.1f}%'
    else:
        return f'L - {gain_pct:.1f}%'



# ✅ Add Squeeze Check column
df['Squeeze Check'] = df.apply(
    lambda row: classify_squeeze(row['Prev Close'], row['High']),
    axis=1
)
def Milli_refitting(shortfloat):
    if pd.isna(shortfloat):
        return None  # or 0 if you want to fill missing values with 0
    return int(float(shortfloat) * 1000000)

df['Float'] = df['Shares Float'].apply(Milli_refitting)

# ✅ Keep only the columns you want — adjust these to match your actual columns!
final_columns = ['Date', 'Ticker', 'Relative Strength Index (14)', 'Relative Volume', 'Performance (Month)', 'Performance (Week)', 'Volatility (Week)', 'Change from Open', 'Gap', 'Float', 'Short Float', 'Short Interest', 'Squeeze Check']

# ✅ If some columns are missing, fill with None to avoid KeyError
for col in final_columns:
    if col not in df.columns:
        df[col] = None

df = df[final_columns]

df['Short Interest'] = df['Short Interest'].apply(Milli_refitting)

print("\n✅ Final DataFrame with Squeeze Check:")
print(df)

# ✅ Save or append to Excel
file_name = 'Short_Interest_Formula_Prediction.xlsx'

if not df.empty:
    if os.path.exists(file_name):
        existing = pd.read_excel(file_name)
        combined_df = pd.concat([existing, df], ignore_index=True)
    else:
        combined_df = df

    combined_df.to_excel(file_name, index=False)
    print(f"\n✅ Data logged to {file_name}")
else:
    print("\n⚠️ No matching tickers found — nothing to log.")