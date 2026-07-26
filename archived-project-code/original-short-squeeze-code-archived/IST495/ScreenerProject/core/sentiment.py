import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from textblob import TextBlob

# Paths to model, vectorizer, and labeled training data
MODEL_PATH = "ScreenerProject/model/sentiment_model.pkl"
VECTORIZER_PATH = "ScreenerProject/model/sentiment_vectorizer.pkl"
LABELED_DATA_PATH = "ScreenerProject/data/labeled_data.csv"

# Classifies a list of headlines using trained model and returns predictions + sentiment score
def classify_headlines(headlines, model, vectorizer):
    if not headlines:
        return pd.DataFrame()
    
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

# Trains a new RandomForest model using labeled headline data
def train_model():
    df = pd.read_csv(LABELED_DATA_PATH, encoding='utf-8')
    X = df['headline']
    y = df['price_movement']

    vectorizer = TfidfVectorizer(stop_words='english')
    X_vec = vectorizer.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vec, y)

    return model, vectorizer

# Loads the model and vectorizer from disk or trains new ones if not found
def train_or_load_model():
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
    except FileNotFoundError:
        model, vectorizer = train_model()
        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)
    return model, vectorizer