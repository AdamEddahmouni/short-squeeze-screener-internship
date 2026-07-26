import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Define your tickers
tickers = ['GME', 'TSLA', 'AMC', 'AAPL', 'NVDA', 'BYSI', 'SLSR', 'STKS', 'GAIN', 'IMMP']

# Excel file name
file_name = 'Options_Data_Log.xlsx'


# Empty list to collect data
records = []

for ticker in tickers:
    print(f"Fetching option data for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        opt_dates = stock.options
        if not opt_dates:
            print(f"No options data available for {ticker}")
            continue

        # Get nearest expiration date
        expiry = opt_dates[0]
        options_chain = stock.option_chain(expiry)

        calls = options_chain.calls
        puts = options_chain.puts

        call_volume = calls['volume'].sum()
        put_volume = puts['volume'].sum()
        pc_ratio = round(put_volume / call_volume, 2) if call_volume else None

        records.append({
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Ticker': ticker,
            'Call Volume': call_volume,
            'Put Volume': put_volume,
            'P/C Ratio': pc_ratio
        })

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

# Save to Excel
df = pd.DataFrame(records)

if os.path.exists(file_name):
    existing = pd.read_excel(file_name)
    frames = [d for d in [existing, df] if not d.empty]
    new_df = pd.concat(frames, ignore_index=True)
else:
    new_df = df

new_df.to_excel(file_name, index=False)
print(f"Options data saved to {file_name}")