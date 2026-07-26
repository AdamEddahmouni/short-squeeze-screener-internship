import requests
import io
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os

FINVIZ_API_KEY = "REDACTED_FINVIZ_KEY_A"  # Replace with your Finviz Elite API key

# 😐 Neutral sentiment indicators
NEUTRAL_KEYWORDS = [
    "announces", "scheduled", "reports", "files", "reveals",
    "unveils", "launch", "releases", "meeting", "statement",
    "introduces", "confirms", "opens", "commences", "names",
    "appoints", "forms", "joins", "listed", "plans", "report", 
    "Fiscal"
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
# 😐 Scrape Finviz for a specific ticker
def fetch_potential_neutral_headlines(ticker):
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

    neutral_headlines = []

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

        if any(kw in headline.lower() for kw in NEUTRAL_KEYWORDS):
            neutral_headlines.append({
                "headline": headline,
                "timestamp": timestamp,
                "url": article_url
            })

        

    return neutral_headlines

# 😐 Use Finviz Elite API for market-wide neutral headlines
def fetch_all_finviz_api_neutral_news():
    url = "https://elite.finviz.com/news_export.ashx?v=3&auth=REDACTED_FINVIZ_KEY_A"  # Replace token
    headers = {
        "Authorization": f"Bearer {FINVIZ_API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        csv_reader = csv.DictReader(io.StringIO(response.text))

        neutral_headlines = []

        for row in csv_reader:
            headline = row.get("Title", "").strip()
            article_url = row.get("Url", "")
            timestamp = row.get("Date", "")

            if any(kw in headline.lower() for kw in NEUTRAL_KEYWORDS):
                neutral_headlines.append({
                    "headline": headline,
                    "timestamp": timestamp,
                    "url": article_url
                })

            

        return neutral_headlines

    except Exception as e:
        print(f"❌ Error accessing Finviz API: {e}")
        return []

# ▶️ Main runner
if __name__ == "__main__":
    ticker = input("Enter stock ticker (or press Enter for market-wide scan): ").strip().upper()

    if not ticker:
        headlines = fetch_all_finviz_api_neutral_news()
    else:
        headlines = fetch_potential_neutral_headlines(ticker)

    if headlines:
        label_headlines_interactively(headlines)
    else:
        print("❌ No headlines found.")
