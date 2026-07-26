import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from textblob import TextBlob

# 🔑 NewsAPI key
API_KEY = '46437b2f8e5045d097b85ddfbd92ced7'  # Replace with your actual key

# 📰 Fetch news by stock ticker
def fetch_news_by_ticker(ticker, page_size=10):
    url = (
        f'https://newsapi.org/v2/everything?q={ticker}'
        f'&pageSize={page_size}&sortBy=publishedAt&language=en&apiKey={API_KEY}'
    )
    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])
    headlines = [article['title'] for article in articles if article.get('title')]
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

# 📊 Classify new headlines
def classify_headlines(headlines, model, vectorizer):
    X_vec = vectorizer.transform(headlines)
    predictions = model.predict(X_vec)
    results = []

    for i, headline in enumerate(headlines):
        sentiment_score = TextBlob(headline).sentiment.polarity
        if -0.05 < sentiment_score < 0.05:
            label = '😐 Neutral'
        else:
            label = '📈 Positive' if predictions[i] == 1 else '📉 Negative'

        results.append({
            'headline': headline,
            'sentiment_score': round(sentiment_score, 3),
            'prediction': label
        })

    return pd.DataFrame(results)

# ▶️ Main
def main():
    ticker = input("Enter a stock ticker (e.g., AAPL, TSLA): ").strip().upper()
    headlines = fetch_news_by_ticker(ticker)

    if not headlines:
        print("❌ No news found for that ticker.")
        return

    print(f"\n🔍 Found {len(headlines)} headlines for {ticker}...")

    model, vectorizer = train_model()
    results_df = classify_headlines(headlines, model, vectorizer)

    print("\n📰 Sentiment Results:\n")
    print(results_df[['headline', 'sentiment_score', 'prediction']])

if __name__ == "__main__":
    main()