import requests
import time
import joblib
import os
import io
import csv
from playsound import playsound  # pip install playsound==1.2.2
from datetime import datetime, time as dt_time
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from winotify import Notification
import webbrowser
import threading
import uuid

# 🔑 Your Finviz Elite API Key
FINVIZ_API_KEY = "REDACTED_FINVIZ_KEY_B"  # Replace with your actual API key



notifier_lock = threading.Lock()

# 🕒 Check if US market is open (Mon–Fri, 9:30am–4:00pm)
def is_market_open():
    now = datetime.now()
    return now.weekday() < 5 and dt_time(9, 30) <= now.time() <= dt_time(16, 0)
    #return True

# 🌐 Fetch all news from Finviz API
def fetch_all_finviz_api_news():
    url = f'https://elite.finviz.com/news_export.ashx?v=3&auth={FINVIZ_API_KEY}'  # Still correct
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


# 🧠 Train or load sentiment model
def train_model():
    df = pd.read_csv("C:/Users/WildB/IST495/Stock-News-ML/data/sample_news.csv", encoding='utf-8')
    X = df['headline']
    y = df['price_movement']

    vectorizer = TfidfVectorizer(stop_words='english')
    X_vec = vectorizer.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vec, y)

    return model, vectorizer

def train_or_load_model():
    try:
        model = joblib.load("model.pkl")
        vectorizer = joblib.load("vectorizer.pkl")
    except FileNotFoundError:
        model, vectorizer = train_model()
        joblib.dump(model, "model.pkl")
        joblib.dump(vectorizer, "vectorizer.pkl")
    return model, vectorizer

# 📊 Classify headlines using ML and sentiment
def classify_headlines(headlines, model, vectorizer):
    X_vec = vectorizer.transform(headlines)
    predictions = model.predict(X_vec)
    prediction_probs = model.predict_proba(X_vec)

    results = []
    for i, headline in enumerate(headlines):
        sentiment_score = TextBlob(headline).sentiment.polarity
        confidence = round(max(prediction_probs[i]), 3)
        label = '📈 Positive' if predictions[i] == 1 else '📉 Negative'

        results.append({
            'headline': headline,
            'sentiment_score': round(sentiment_score, 3),
            'prediction': label,
            'confidence_score': confidence
        })

    return pd.DataFrame(results)

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