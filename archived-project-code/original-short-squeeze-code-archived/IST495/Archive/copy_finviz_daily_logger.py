import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# List of tickers to track
tickers = ['GME', 'TSLA', 'AMC', 'AAPL', 'NVDA', 'BYSI', 'SLSR', 'STKS', 'GAIN', 'IMMP']

# Columns you want in your Excel file
columns = [
    'Date', 'Ticker', 'Short Rat', 'RSI(14D)', 'Rel Vol',
    'Perf (M)'
]

# Excel file name
file_name = 'Short_Interest_Formula_Prediction.xlsx'

# Helper function to parse Finviz data
def get_stock_data(ticker):
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    data = {col: None for col in columns}
    data['Date'] = datetime.now().strftime('%Y-%m-%d')
    data['Ticker'] = ticker

    table = soup.find('table', class_='snapshot-table2')
    rows = table.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        for i in range(0, len(cells), 2):
            key = cells[i].text
            val = cells[i + 1].text

           
            if key == 'Short Ratio':
                data['Short Rat'] = val
            elif key == 'RSI (14)':
                data['RSI(14D)'] = val
            elif key == 'Rel Volume':
                data['Rel Vol'] = val
            elif key == 'Perf Month':
                data['Perf (M)'] = val
            elif key == 'Shs Float':
                data['Float'] = val
           

    return data

# Collect data for each ticker
records = []
for ticker in tickers:
    try:
        print(f'Fetching {ticker}...')
        data = get_stock_data(ticker)
        records.append(data)
    except Exception as e:
        print(f'Error fetching {ticker}: {e}')

# Convert to DataFrame
df = pd.DataFrame(records)

# Write or append to Excel
if os.path.exists(file_name):
    existing = pd.read_excel(file_name)
    new_df = pd.concat([existing, df], ignore_index=True)
else:
    new_df = df

new_df.to_excel(file_name, index=False)
print(f'Data logged to {file_name}')