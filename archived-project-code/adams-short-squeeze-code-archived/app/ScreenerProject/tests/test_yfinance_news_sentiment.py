import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.yfinance_news_api import fetch_yfinance_news
from core.sentiment import train_or_load_model, classify_headlines

# Known-volatile/high-news-volume tickers, useful for manually sanity-checking
# sentiment output against real headlines regardless of screener discovery status.
TEST_TICKERS = ["GME", "AMC", "KOSS", "BBBY", "TSLA"]


def main():
    print(f"Fetching yfinance news for {TEST_TICKERS}...")
    news = fetch_yfinance_news(TEST_TICKERS)

    if not news:
        print("⚠️ No headlines returned — check network access or yfinance's .news endpoint.")
        return

    print(f"✅ Fetched {len(news)} headline(s)")

    print("Loading sentiment model...")
    model, vectorizer = train_or_load_model()

    headlines = [item["headline"] for item in news]
    df = classify_headlines(headlines, model, vectorizer)

    for i, row in df.iterrows():
        item = news[i]
        print(f"\n📰 {row['headline']}")
        print(f"   Ticker: {', '.join(item['tickers'])}")
        print(f"   Prediction: {row['prediction']} (confidence {row['confidence_score']})")
        print(f"   TextBlob polarity: {row['sentiment_score']}")
        print(f"   URL: {item['url']}")


if __name__ == "__main__":
    main()
