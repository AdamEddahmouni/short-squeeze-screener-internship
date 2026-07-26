import requests
import time
import joblib
import os
from playsound import playsound  # pip install playsound==1.2.2
from datetime import datetime, time as dt_time
from textblob import TextBlob
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# 📰 Fetch news by stock ticker
def fetch_news_by_ticker(ticker, max_articles=10):
    from urllib.parse import urljoin

    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    news_table = soup.find("table", class_="fullview-news-outer")
    if not news_table:
        return []

    headlines = []
    for row in news_table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 2:
            continue

        link_tag = cols[1].find("a")
        if not link_tag:
            continue

        timestamp_text = cols[0].get_text(strip=True)
        headline = link_tag.get_text(strip=True)
        article_url = urljoin("https://finviz.com/", link_tag.get("href", ""))

        headlines.append({
            "headline": headline,
            "timestamp": timestamp_text,
            "url": article_url
        })

        if len(headlines) >= max_articles:
            break

    return headlines

# 🧠 Train model using TF-IDF features
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

# 📊 Classify headlines
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

# ⏰ Market open checker
def is_market_open():
    now = datetime.now()
    return now.weekday() < 5 and dt_time(9, 30) <= now.time() <= dt_time(16, 0)

# 🔔 Run alert loop
def run_alert_loop(ticker, model, vectorizer):
    seen_headlines = set()
    print(f"📡 Monitoring {ticker} news on Finviz...")

    while True:
        if not is_market_open():
            print("⏸ Market closed. Waiting 60s...")
            time.sleep(60)
            continue

        headlines = fetch_news_by_ticker(ticker)
        new_headlines = [h for h in headlines if h["headline"] not in seen_headlines]

        if new_headlines:
            texts = [h["headline"] for h in new_headlines]
            df = classify_headlines(texts, model, vectorizer)

            for i, row in df.iterrows():
                if row['prediction'] == '📈 Positive' and row['confidence_score'] >= 0.6:
                    print(f"\n🔔 ALERT: Positive News for {ticker}")
                    print(f"📰 {row['headline']}")
                    print(f"📊 Confidence: {row['confidence_score']} | Sentiment: {row['sentiment_score']}")
                    print(f"🔗 URL: {new_headlines[i]['url']}")
                    playsound("alert.mp3")  # Ensure this file exists

                seen_headlines.add(row['headline'])

        time.sleep(60)

# ▶️ Main interactive mode
def main():
    model, vectorizer = train_or_load_model()

    while True:
        ticker = input("\nEnter a stock ticker to monitor live (or 'Q' to quit): ").strip().upper()
        if ticker == "Q":
            print("👋 Exiting the program.")
            break

        run_alert_loop(ticker, model, vectorizer)

if __name__ == "__main__":
    main()