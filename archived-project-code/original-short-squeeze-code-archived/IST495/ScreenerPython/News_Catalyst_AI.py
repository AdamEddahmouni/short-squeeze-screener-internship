import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer


# 📰 Fetch news by stock ticker
def fetch_news_by_ticker(ticker, max_articles=5):
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
    today = datetime.now().date()
    fallback_headline = None

    for row in news_table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 2:
            continue

        link_tag = cols[1].find("a")
        if not link_tag:
            continue

        headline = link_tag.get_text(strip=True)
        article_url = urljoin("https://finviz.com/", link_tag.get("href", ""))
        timestamp_text = cols[0].get_text(strip=True)
        now = datetime.now()

        try:
            if " " in timestamp_text:
                # Format: 'Jun-05-25 08:30AM' or similar
                timestamp_obj = datetime.strptime(timestamp_text, "%b-%d-%y %I:%M%p")
            else:
                timestamp_obj = datetime.strptime(timestamp_text, "%I:%M%p")
                timestamp_obj = now.replace(hour=timestamp_obj.hour, minute=timestamp_obj.minute, second=0, microsecond=0)
        except ValueError:
            continue  # skip if date format is wrong

        headline_data = {
            "headline": headline,
            "timestamp": timestamp_obj.strftime("%Y-%m-%d %H:%M"),
            "timestamp_obj": timestamp_obj,
            "url": article_url
        }

        if timestamp_obj.date() == today:
            headlines.append(headline_data)
        elif not fallback_headline:
            fallback_headline = headline_data

        if len(headlines) >= max_articles:
            break

    if len(headlines) < 1 and fallback_headline:
        fallback_headline["headline"] += f" (📌 Last headline posted on {fallback_headline['timestamp']})"
        headlines.append(fallback_headline)

    return headlines

# 🧠 Train model using TF-IDF features
def train_model():
    df = pd.read_csv("Stock-News-ML/data/sample_news.csv", encoding='utf-8')
    X = df['headline']
    y = df['price_movement']

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    X_vec = vectorizer.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vec, y)

    return model, vectorizer

# 📊 Classify new headlines
def classify_headlines(headlines, model, vectorizer):
    X_vec = vectorizer.transform(headlines)
    prediction_probs = model.predict_proba(X_vec)
    predictions = model.predict(X_vec)
    results = []

    net_score = 0

    for i, headline in enumerate(headlines):
        sentiment_score = TextBlob(headline).sentiment.polarity
        label = '😐 Neutral'
        confidence = prediction_probs[i][1]  # probability of class 1 (positive)
        
        if predictions[i] == 1:
            label = '📈 Positive'
            net_score += confidence
        else:
            label = '📉 Negative'
            net_score -= confidence

        results.append({
            'headline': headline,
            'sentiment_score': round(sentiment_score, 3),
            'prediction': label,
            'model_confidence': round(confidence, 3)
        })

    # Normalize score
    net_score = net_score / len(headlines)
    net_prediction = '📈 Likely Positive' if net_score > 0 else '📉 Likely Negative'

    # Determine confidence level
    abs_score = abs(net_score)
    if abs_score < 0.2:
        confidence_level = 'Low Confidence'
    elif abs_score < 0.4:
        confidence_level = 'Medium Confidence'
    elif abs_score < 0.6:
        confidence_level = 'High Confidence'
    else:
        confidence_level = 'Very High Confidence'

    overall = {
        'net_score': round(net_score, 3),
        'overall_prediction': net_prediction,
        'confidence_level': confidence_level
    }

    return pd.DataFrame(results), overall

# ▶️ Main
def main():
    ticker = input("Enter a stock ticker (e.g., AAPL, TSLA): ").strip().upper()
    headlines = fetch_news_by_ticker(ticker)

    if not headlines:
        print("❌ No news found for that ticker.")
        return

    print(f"\n🔍 Found {len(headlines)} headlines for {ticker}...")

    # Filter for today's headlines
    today = datetime.now().date()
    todays_headlines = [h for h in headlines if datetime.strptime(h["timestamp_obj"].strftime("%Y-%m-%d"), "%Y-%m-%d").date() == today]

    model, vectorizer = train_model()
    headlines_text = [item["headline"] for item in headlines]
    results_df, overall = classify_headlines(headlines_text, model, vectorizer)

    # Add timestamp and url columns
    results_df["timestamp"] = [item["timestamp"] for item in headlines]
    results_df["url"] = [item["url"] for item in headlines]

    print("\n📰 Sentiment Results:\n")
    print(results_df[['headline', 'prediction', 'model_confidence', 'timestamp', 'url']])

    if len(todays_headlines) >= 5:
        print("\n📈 Final Prediction Summary:")
        print(f"   ➤ Outcome: {overall['overall_prediction']}")
        print(f"   ➤ Net Score: {overall['net_score']}")
        print(f"   ➤ Confidence Level: {overall['confidence_level']}")
    else:
        # Show last article time as footnote
        if headlines:
            print(f"\n📝 Note: Less than 5 articles released today. Last headline posted: {headlines[0]['timestamp']}")
if __name__ == "__main__":
    main()