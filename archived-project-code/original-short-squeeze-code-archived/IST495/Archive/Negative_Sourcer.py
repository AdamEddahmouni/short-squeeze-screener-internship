import requests
import io
import csv
from datetime import datetime, time as dt_time
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os

FINVIZ_API_KEY = "750b45bf-5158-4678-b841-b695656321df"  # Replace with your actual API key

NEGATIVE_KEYWORDS = [
    "misses", "falls", "drops", "plunges", "declines", "loss", "downgraded", "warning",
    "lawsuit", "recall", "bankruptcy", "fraud", "scandal", "resigns", "investigation",
    "delay", "shutdown", "missed expectations", "underperforms", "cut", "layoffs", "fined",
    "miss", "downgrade", "cuts", "furloughs", "downsizing", "job cuts", "reductions", "restructuring"
]

def label_headlines_interactively(headlines, csv_path="Stock-News-ML/data/sample_news.csv"):
    print("\n🧠 Interactive Headline Labeling Mode")
    print("Type:  1 = Positive, 0 = Neutral, -1 = Negative, N = Skip, Q = Quit\n")

    if not headlines:
        print("No headlines available to label.")
        return

    # Ensure the file exists and has headers
    file_exists = os.path.exists(csv_path)
    if not file_exists:
        with open(csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["headline", "price_movement"])
            writer.writeheader()

    for item in headlines:
        print(f"\n📰 {item['headline']}")
        print(f"⏰ {item['timestamp']}")
        print(f"🔗 {item['url']}")
        
        while True:
            label = input("Label (1/0/-1/N/Q): ").strip().upper()
            if label in {"1", "0", "-1"}:
                with open(csv_path, "a", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["headline", "price_movement"])
                    writer.writerow({"headline": item["headline"], "price_movement": label})
                break
            elif label == "N":
                print("⏭️ Skipped.")
                break
            elif label == "Q":
                print("👋 Exiting labeling mode.")
                return
            else:
                print("❗ Invalid input. Please enter 1, 0, -1, N or Q.")

# ✅ Scrape Finviz website (no API) for a ticker
def fetch_potential_negative_headlines(ticker, max_headlines=15):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching page for {ticker}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    news_table = soup.find("table", class_="fullview-news-outer")
    if not news_table:
        return []

    negative_headlines = []

    for row in news_table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 2:
            continue

        link_tag = cols[1].find("a")
        if not link_tag:
            continue

        headline = link_tag.get_text(strip=True)
        article_url = urljoin("https://finviz.com/", link_tag.get("href", ""))
        timestamp = cols[0].get_text(strip=True)

        if any(kw in headline.lower() for kw in NEGATIVE_KEYWORDS):
            negative_headlines.append({
                "headline": headline,
                "timestamp": timestamp,
                "url": article_url
            })

        if len(negative_headlines) >= max_headlines:
            break

    return negative_headlines

# ✅ Use Finviz Elite API to get all recent news, filtered for negatives
def fetch_all_finviz_api_news(max_headlines=20):
    url = "https://elite.finviz.com/news_export.ashx?v=3&auth=750b45bf-5158-4678-b841-b695656321df"  # Replace `*****` with your actual token
    headers = {
        "Authorization": f"Bearer {FINVIZ_API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        csv_reader = csv.DictReader(io.StringIO(response.text))

        negative_headlines = []

        for row in csv_reader:
            headline = row.get("Title", "").strip()
            article_url = row.get("Url", "")
            timestamp = row.get("Date", "")

            if any(kw in headline.lower() for kw in NEGATIVE_KEYWORDS):
                negative_headlines.append({
                    "headline": headline,
                    "timestamp": timestamp,
                    "url": article_url
                })

            if len(negative_headlines) >= max_headlines:
                break

        return negative_headlines

    except Exception as e:
        print(f"❌ Error accessing Finviz API: {e}")
        return []

# ▶️ Example usage

if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
    if ticker == "":
        print(f"\n 📰 Suggested Market Wide Negative Headlines")
        headlines = fetch_all_finviz_api_news()
        for item in headlines:
            print(f"- {item['headline']} ({item['timestamp']})\n  {item['url']}\n")

    
    else:
        headlines = fetch_potential_negative_headlines(ticker)
        if headlines:
            print(f"\n📰 Suggested Negative Headlines for {ticker}:\n")
            for item in headlines:
                print(f"- {item['headline']} ({item['timestamp']})\n  {item['url']}\n")
        else:
            print("❌ No negative headlines found.")