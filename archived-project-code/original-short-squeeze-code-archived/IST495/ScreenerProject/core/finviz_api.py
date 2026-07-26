import pandas as pd
import requests
import io
import csv

# Replace this with your actual API token
FINVIZ_API_KEY = "YOUR API TOKEN HERE"

# Fetches live Finviz screener CSV data using the Elite export endpoint
def fetch_finviz_data():
    full_url = f"https://elite.finviz.com/export.ashx?v=152&f=sh_float_u20,sh_price_u20&c=1,25,26,30,31,84,42,43,49,50,52,53,55,56,57,59,60,61,64,81,86,87,65,66&auth={FINVIZ_API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(full_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

    # Parse CSV response into a DataFrame
    df = pd.read_csv(io.StringIO(response.text))
    return df

# Fetches all breaking news headlines and related metadata from Finviz API
def fetch_all_finviz_api_news():
    url = f'https://elite.finviz.com/news_export.ashx?v=3&auth={FINVIZ_API_KEY}'
    headers = {
        "Authorization": f"Bearer {FINVIZ_API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        csv_text = response.text
        csv_reader = csv.DictReader(io.StringIO(csv_text))

        headlines = []
        for row in csv_reader:
            tickers = row.get("Ticker", "").strip()
            ticker_list = [t.strip() for t in tickers.split(",")] if tickers else []

            headlines.append({
                "headline": row.get("Title", "No title"),
                "timestamp": row.get("Date", "Unknown time"),
                "url": row.get("Url", ""),
                "tickers": ticker_list
            })

        return headlines
    except Exception as e:
        print(f"❌ Error fetching news from Finviz API: {e}")
        return []
