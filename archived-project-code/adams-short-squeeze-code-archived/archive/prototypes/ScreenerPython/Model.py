import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from textblob import TextBlob
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

class ScreenerModel:
    def __init__(self):
        self.ticker_symbol = ""
        self.stock_data = {}
        self.vectorizer = None
        self.model = None

    def set_ticker_symbol(self, symbol):
        self.ticker_symbol = symbol

    def get_ticker_symbol(self):
        return self.ticker_symbol

    def get_stock_data(self):
        return self.stock_data

    def fetch_news_by_ticker(self, max_articles=5):
        from urllib.parse import urljoin

        url = f"https://finviz.com/quote.ashx?t={self.ticker_symbol}"
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

    def fetch_finviz_data(self):
        try:
            url = f"https://finviz.com/quote.ashx?t={self.ticker_symbol}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.select_one(".snapshot-table2")
            data = {}

            for row in table.select("tr"):
                cells = row.select("td")
                for i in range(0, len(cells), 2):
                    key = cells[i].text.strip()
                    value = cells[i + 1].text.strip()
                    if key in ["Price", "Change", "Rel Volume", "Shs Float"]:
                        if key == "Rel Volume":
                            data["Rel Vol"] = value
                        elif key == "Shs Float":
                            data["Float"] = value
                        else:
                            data[key] = value

            self.stock_data = data
        except Exception as e:
            print(f"Error fetching data: {e}")
            self.stock_data = {}

    def train_news_model(self):
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

    def analyze_news(self):
        self.model, self.vectorizer = self.train_news_model()
        self.train_news_model()
        headlines = self.fetch_news_by_ticker()
        if not headlines:
            return {"overall_prediction": "No News", "net_score": 0, "confidence_level": "N/A"}

        texts = [item["headline"] for item in headlines]
        X_vec = self.vectorizer.transform(texts)
        predictions = self.model.predict(X_vec)
        probs = self.model.predict_proba(X_vec)

        net_score = 0
        for i, _ in enumerate(texts):
            confidence = probs[i][1]
            net_score += confidence if predictions[i] == 1 else -confidence

        net_score /= len(texts)
        overall_prediction = "📈 Likely Positive" if net_score > 0 else "📉 Likely Negative"

        abs_score = abs(net_score)
        if abs_score < 0.2:
            confidence = "Low Confidence"
        elif abs_score < 0.4:
            confidence = "Medium Confidence"
        elif abs_score < 0.6:
            confidence = "High Confidence"
        else:
            confidence = "Very High Confidence"

        return {
            "overall_prediction": overall_prediction,
            "net_score": round(net_score, 3),
            "confidence_level": confidence
        }


