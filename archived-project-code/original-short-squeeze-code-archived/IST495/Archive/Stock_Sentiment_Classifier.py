import requests
import time
import joblib
import os
from playsound import playsound  # pip install playsound==1.2.2
from datetime import datetime, time as dt_time
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# 🕒 Check if US market is open (Mon–Fri, 9:30am–4:00pm)
def is_market_open():
    now = datetime.now()
    return now.weekday() < 5 and dt_time(8, 30) <= now.time() <= dt_time(16, 0)

# 🌐 Fetch all news from Finviz News page
def fetch_all_finviz_news():
    url = "https://finviz.com/news.ashx?v=3"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    headlines = []
    table = soup.find("table", class_="t-home-table")
    if not table:
        return []

    for row in table.find_all("tr"):
        time_cell = row.find("td", class_="nn-date")
        text_cell = row.find("a")

        if not time_cell or not text_cell:
            continue

        timestamp_text = time_cell.get_text(strip=True)
        headline_text = text_cell.get_text(strip=True)
        url = "https://finviz.com" + text_cell.get("href")

        headlines.append({
            "headline": headline_text,
            "timestamp": timestamp_text,
            "url": url
        })

    return headlines

# 🧠 Train or load sentiment model
def train_model():
    df = pd.read_csv("Stock-News-ML/data/sample_news.csv", encoding='utf-8')
    X = df['headline']
    y = df['price_movement']

    vectorizer = TfidfVectorizer(stop_words='english')
    X_vec = vectorizer.fit_transform(X)

    model = LogisticRegression()
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

# 🔔 Main monitoring loop
def run_finviz_news_monitor(model, vectorizer):
    seen_headlines = set()
    print("📡 Monitoring ALL Finviz market news during open hours...")

    while True:
        if not is_market_open():
            print("⏸ Market is closed. Waiting 60s...")
            time.sleep(60)
            continue

        all_news = fetch_all_finviz_news()
        new_news = [item for item in all_news if item["headline"] not in seen_headlines]

        if new_news:
            texts = [item["headline"] for item in new_news]
            df = classify_headlines(texts, model, vectorizer)

            for i, row in df.iterrows():
                if row['prediction'] == '📈 Positive' and row['confidence_score'] >= 0.4:
                    print(f"\n🔔 ALERT: Market-Wide Positive News")
                    print(f"📰 {row['headline']}")
                    print(f"📊 Confidence: {row['confidence_score']} | Sentiment: {row['sentiment_score']}")
                    print(f"🔗 URL: {new_news[i]['url']}")
                    try:
                        playsound("alert.mp3")  # make sure alert.mp3 is in your project folder
                    except Exception as e:
                        print(f"⚠️ Error playing sound: {e}")

                seen_headlines.add(row['headline'])

        else:
            print("✅ No new headlines.")
        
        time.sleep(60)

# ▶️ Entry point
def main():
    model, vectorizer = train_or_load_model()
    run_finviz_news_monitor(model, vectorizer)

if __name__ == "__main__":
    main()