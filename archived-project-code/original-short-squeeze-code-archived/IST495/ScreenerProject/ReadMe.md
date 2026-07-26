# 🧠 Stock Screener with Sentiment Analysis

A live short squeeze screener that pulls real-time data from Finviz Elite, applies AI-driven news sentiment classification, and auto-calculates price targets and stop-losses.

---

## 🚀 Features

- ✅ Real-time Finviz Elite integration
- ✅ Custom filters for float, price, % change, short float, and relative volume
- ✅ AI-powered sentiment analysis on breaking news headlines
- ✅ Color-coded GUI with Prime vs Subprime setup detection
- ✅ Automatic logging of top setups
- ✅ Target and stop-loss calculation using volatility and RSI
- ✅ Loadable stock graphs reflecting live data
- ✅ Breaking News Tab that displays articles in real time with predicted positive impact

---

## ⚠️ Common Troubleshooting Issues

- If there is an issue with the breaking news not loading make sure that in the sentiment.py file the MODEL_PATH, VECTORIZER_PATH, and LABELED_DATA_PATH are all mapped correctly (Lines 8-10). If necessary map them using each file's absolute path. 


## 📦 Installation

1. Clone or download the repo  
2. Create virtual environment *(optional but recommended)*  
3. Install requirements:
    In your terminal run
        pip install -r requirements.txt
    - This app uses Tkinter for the GUI. Tkinter comes pre-installed with most Python distributions.
    If you're on Linux and it's missing, install it via:
        Debian/Ubuntu: sudo apt-get install python3-tk
        Fedora: sudo dnf install python3-tkinter

- Tested on Python 3.10

## ▶️ Running the App

run file: main.py
    Make sure you’ve added your Finviz Elite API key in core/finviz_api.py. line 7

* Finviz Elite Membership Required for API token

## 📁 Project Structure

ScreenerProject/
├── core/
│   ├── filters.py
│   ├── finviz_api.py
│   └── sentiment.py
├── controller/
│   └── controller.py
├── ui/
│   └── view.py
├── model/
│   ├── sentiment_model.pkl
│   └── sentiment_vectorizer.pkl
├── tests/
│   └── test_filters.py
├── data/
│   ├── labeled_data.csv
│   └── prime_log.csv
├── main.py
├── requirements.txt
└── README.md


## ⚙️ Filter Logic
Price: $2–$20

Float: < 20M

Change: ≥ +10%

Relative Volume: ≥ 5.0

Short Float: ≥ 5%


## 🧠 Sentiment Model
Uses RandomForestClassifier

Headlines vectorized with TF-IDF

Confidence score and sentiment label applied per headline

## 🗃️ Logging
Logs all 5/5 Prime setups to:

logs/prime_log.csv
Ensures no duplicate ticker is logged more than once per day.

## 📈 Target / Stop-Loss Formula
Target = 0.7 × Volatility + 0.03 × (70 - RSI)

Stop = 0.3 × Volatility - 0.02 × (RSI - 50)

## 👨‍💻 Author
Built by William Gray as part of an internship/independent research project using Finviz Elite, Python, and machine learning.

# 📝 License
Free to use and modify.