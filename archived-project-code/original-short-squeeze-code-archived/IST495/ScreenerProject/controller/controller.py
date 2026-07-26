import csv
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from core.sentiment import train_or_load_model, classify_headlines
from core.finviz_api import fetch_all_finviz_api_news
import webbrowser
from core.filters import rank_and_group_stocks


class Controller:

    # Logs a prime ticker to the prime_log.csv file if not already logged today
    def log_prime_ticker(ticker_data):
        os.makedirs("logs", exist_ok=True)
        log_path = "ScreenerProject/data/prime_log.csv"
        fields = ["timestamp", "ticker", "price", "target", "stop_loss", "sentiment"]
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker_data.get("Ticker"),
            "price": ticker_data.get("Price"),
            "target": ticker_data.get("Target"),
            "stop_loss": ticker_data.get("StopLoss"),
            "sentiment": ticker_data.get("Sentiment", "")
        }

        # Avoid duplicates
        if os.path.exists(log_path):
            with open(log_path, "r", newline="", encoding="utf-8") as f:
                today = datetime.now().date()

                for row in csv.DictReader(f):
                    row_date = datetime.fromisoformat(row["timestamp"]).date()

                    if row["ticker"] == new_entry["ticker"] and row_date == today:
                        return  # Already logged today
                    
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)

            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(new_entry)

    # Loads the sentiment model and cached news headlines from Finviz
    def __init__(self):
        self.model, self.vectorizer = train_or_load_model()
        self.news_cache = fetch_all_finviz_api_news()

    # Generates formatted screener results for Prime and Subprime setups with sentiment
    def get_screener_results(self):
        prime, subprime = rank_and_group_stocks()
        results = []

        def classify_batch(batch):
            formatted = []
            for stock in batch:
                ticker = stock.get('Ticker', '')
                headline = ""

                # ✅ Match to a news headline
                for news in self.news_cache:

                    if ticker in news.get("tickers", []):
                        headline = news.get("headline", "")
                        break

                sentiment = ""

                if self.model and headline:
                    df = classify_headlines([headline], self.model, self.vectorizer)

                    if not df.empty:
                        sentiment = f"{df.iloc[0]['prediction']} ({int(df.iloc[0]['confidence_score']*100)}%)"
                
                formatted.append([
                    ticker,
                    stock.get("Price", "?"),
                    stock.get("Float", "?"),
                    stock.get("RelVolume", "?"),
                    stock.get("ChangePercent", "?"),
                    stock.get("Target", "?"),
                    stock.get("StopLoss", "?"),
                    sentiment
                ])

            return formatted

        for stock in prime:
            ticker = stock.get('Ticker', '')
            headline = ""

            for news in self.news_cache:
                if ticker in news.get("tickers", []):
                    headline = news.get("headline", "")
                    break

            sentiment = ""
            if self.model and headline:
                df = classify_headlines([headline], self.model, self.vectorizer)

                if not df.empty:
                    sentiment = f"{df.iloc[0]['prediction']} ({int(df.iloc[0]['confidence_score']*100)}%)"

            stock["Sentiment"] = sentiment
            Controller.log_prime_ticker(stock)

        prime_results = classify_batch(prime)
        subprime_results = classify_batch(subprime)
        return prime_results, subprime_results

    """# Classifies a single custom headline
    def classify_single_headline(self, headline):
        if not self.model:
            return None
        
        df = classify_headlines([headline], self.model, self.vectorizer)
        return df.iloc[0] if not df.empty else None"""

    # Returns a list of high-confidence positive headlines from the cached news
    def get_positive_news(self):
        if not self.model:
            return []
        
        news = self.news_cache
        headlines = [item['headline'] for item in news]
        df = classify_headlines(headlines, self.model, self.vectorizer)
        positive = []
        for i, row in df.iterrows():
            if "Positive" in row['prediction'] and row['confidence_score'] >= 0.6:
                positive.append({
                    "headline": row['headline'],
                    "confidence_score": row['confidence_score'],
                    "tickers": news[i].get("tickers", []),
                    "url": news[i].get("url", "")
                })
                
        return positive

    # Opens a URL in the default web browser
    def open_url(self, url):
        webbrowser.open_new_tab(url)
