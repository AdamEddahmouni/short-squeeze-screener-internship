import os
import pandas as pd
import requests
import io
import csv
from dotenv import load_dotenv

# Loaded here (not just in main.py) for the same reason as newsapi_news_api.py/
# finnhub_api.py - FINVIZ_API_KEY needs to be populated regardless of entry point.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Blank by default (was previously a hardcoded "YOUR API TOKEN HERE" placeholder
# literal, inconsistent with every other key in this codebase) - set FINVIZ_API_KEY
# in .env directly, or run core/finviz_auth.py to fetch it automatically from a
# real Finviz Elite login. controller.py's _should_use_finviz() treats a blank
# value as "no real key configured" the same way it already does for NEWSAPI_KEY.
FINVIZ_API_KEY = os.environ.get("FINVIZ_API_KEY", "")

# Fetches live Finviz screener CSV data using the Elite export endpoint. Uses
# the current /export/screener path (confirmed 2026-07-09 via Finviz's own
# api_explanation page) rather than the legacy export.ashx - both work
# (export.ashx 301-redirects to the new path, and requests.get() follows
# redirects by default), but pointing at the documented-current path directly
# avoids relying on that implicit behavior.
def fetch_finviz_data():
    full_url = f"https://elite.finviz.com/export/screener?v=152&f=sh_float_u20,sh_price_u20&c=1,25,26,30,31,84,42,43,49,50,52,53,55,56,57,59,60,61,64,81,86,87,65,66&auth={FINVIZ_API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(full_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

    # Parse CSV response into a DataFrame
    df = pd.read_csv(io.StringIO(response.text))
    return df

# Fetches all breaking news headlines and related metadata from Finviz API.
# Still on the legacy news_export.ashx path - Finviz's docs only confirmed the
# screener endpoint's new /export/screener path, not a news equivalent, so this
# is left as-is rather than guessing at an unconfirmed URL. Works either way
# via requests.get()'s default redirect-following if Finviz applies the same
# migration here too.
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
