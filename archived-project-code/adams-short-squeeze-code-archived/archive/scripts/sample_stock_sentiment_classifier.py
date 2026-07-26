import pandas as pd
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

# Step 1: Load data
df = pd.read_csv("Stock-News-ML/data/sample_news.csv", encoding='utf-8')

# Step 2: Add sentiment score
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

df['sentiment'] = df['headline'].apply(get_sentiment)

# Step 3: Prepare data
X = df[['sentiment']]  # Feature: sentiment score
y = df['price_movement']  # Label

# Step 4: Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 5: Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Step 6: Make predictions
y_pred = model.predict(X_test)

# Step 7: Evaluate model
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Step 8: Visualize
plt.scatter(df['sentiment'], df['price_movement'], c='blue')
plt.axhline(0, color='red', linestyle='--')
plt.title("Sentiment vs Price Movement")
plt.xlabel("Sentiment Score")
plt.ylabel("Price Movement")
plt.grid(True)
plt.show()