import requests
import time
import os
import io
import csv
import sys
from playsound import playsound  # pip install playsound==1.2.2
from datetime import datetime, time as dt_time
from winotify import Notification
import webbrowser
import threading
import uuid

# core/sentiment.py is the canonical train_or_load_model/classify_headlines implementation
# (now FinBERT-backed); this script used to carry its own byte-for-byte copy, which is why
# it's imported here instead of duplicated.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app", "ScreenerProject"))
from core.sentiment import classify_headlines, train_or_load_model

# 🔑 Your Finviz Elite API Key
FINVIZ_API_KEY = "YOUR API TOKEN HERE"  # dead key archived: archive/legacy-data/deprecated_api_keys.md



notifier_lock = threading.Lock()

# 🕒 Check if US market is open (Mon–Fri, 9:30am–4:00pm)
def is_market_open():
    now = datetime.now()
    return now.weekday() < 5 and dt_time(9, 30) <= now.time() <= dt_time(16, 0)
    #return True

# 🌐 Fetch all news from Finviz API
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


# 📁 Save flagged articles
def log_flagged_article(article, prediction_row):
    with open("flagged_articles_log.txt", "a", encoding="utf-8") as f:
        f.write("🔔 FLAGGED ARTICLE\n")
        f.write(f"🕒 Time: {article['timestamp']}\n")
        f.write(f"📰 Title: {article['headline']}\n")
        f.write(f"📊 Tickers: {', '.join(article.get('tickers', [])) or 'N/A'}\n")
        f.write(f"🔗 URL: {article['url']}\n")
        f.write(f"📈 Confidence Score: {prediction_row['confidence_score']}\n")
        f.write(f"💬 Sentiment Score: {prediction_row['sentiment_score']}\n")
        f.write("-" * 60 + "\n")

# 🛎️ Desktop pop-up
def show_notification(title, msg, url):
    try:
        toast = Notification(
            app_id="Stock News Alert",
            title=title,
            msg=msg,
            icon="C:/Users/WildB/IST495/icon.png",  # ✅ Path to your icon file
            duration="short"
        )

        toast.add_actions(label="Open Article", launch=url)
        toast.show()
    except Exception as e:
        print(f"⚠️ Notification error: {e}")
# 🔁 Monitoring loop
def run_finviz_news_monitor(model, vectorizer):
    seen_headlines = set()
    print("📡 Monitoring Finviz API news during open hours...")

    while True:

        new_news = []

        if not is_market_open():
            print("⏸ Market is closed. Fetching After Hours or Pre-Market News ")
            all_news = fetch_all_finviz_api_news()
            new_news = [item for item in all_news if item["headline"] not in seen_headlines]
        
        if new_news:
            texts = [item["headline"] for item in new_news]
            df = classify_headlines(texts, model, vectorizer)

            for i, row in df.iterrows():
                if row['prediction'] == '📈 Positive' and row['confidence_score'] >= 0.7:
                    print(f"\n🔔 ALERT: Positive News 📈")
                    print(f"📰 {row['headline']}")
                    print(f"📊 Confidence: {row['confidence_score']} | Sentiment: {row['sentiment_score']}")
                    tickers = ", ".join(new_news[i].get("tickers", []))
                    print(f"📊 Tickers: {tickers if tickers else 'N/A'}")
                    print(f"🔗 URL: {new_news[i]['url']}")
                    
                    # 🔔 Trigger notification
                    show_notification(
                        title="📈 Stock News Alert",
                        msg=f"{row['headline']} [{tickers}]",
                        url=new_news[i]['url']
                    )

                    time.sleep(1.5)

                    # 💾 Log the article
                    log_flagged_article(new_news[i], row)

                    # 🔊 Play sound
                    try:
                        playsound("C:/Users/WildB/IST495/Stock-News-ML/alert.mp3")
                    except Exception as e:
                        print(f"⚠️ Error playing sound: {e}")

                seen_headlines.add(row['headline'])

            time.sleep(600)
            continue

        all_news = fetch_all_finviz_api_news()
        new_news = [item for item in all_news if item["headline"] not in seen_headlines]

        if new_news:
            texts = [item["headline"] for item in new_news]
            df = classify_headlines(texts, model, vectorizer)

            for i, row in df.iterrows():
                if row['prediction'] == '📈 Positive' and row['confidence_score'] >= 0.6:
                    print(f"\n🔔 ALERT: Positive News 📈")
                    print(f"📰 {row['headline']}")
                    print(f"📊 Confidence: {row['confidence_score']} | Sentiment: {row['sentiment_score']}")
                    tickers = ", ".join(new_news[i].get("tickers", []))
                    print(f"📊 Tickers: {tickers if tickers else 'N/A'}")
                    print(f"🔗 URL: {new_news[i]['url']}")
                    
                    # 🔔 Trigger notification
                    show_notification(
                        title="📈 Stock News Alert",
                        msg=f"{row['headline']} [{tickers}]",
                        url=new_news[i]['url']
                    )

                    time.sleep(1.5)

                    # 💾 Log the article
                    log_flagged_article(new_news[i], row)

                    # 🔊 Play sound
                    try:
                        playsound("C:/Users/WildB/IST495/Stock-News-ML/alert.mp3")
                    except Exception as e:
                        print(f"⚠️ Error playing sound: {e}")

                seen_headlines.add(row['headline'])

        time.sleep(30)

# ▶️ Entry
def main():
    model, vectorizer = train_or_load_model()
    run_finviz_news_monitor(model, vectorizer)

if __name__ == "__main__":
    main()