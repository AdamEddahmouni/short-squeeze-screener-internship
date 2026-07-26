import pandas as pd
import yfinance as yf


def fetch_chart_data(ticker, period="5d", interval="30m"):
    """Intraday close-price history for a ticker, as JSON-serializable points.

    Same yfinance call ui/view.py's plot_chart() uses for the Tkinter Chart tab
    (5-day/30-min), just returned as data instead of a matplotlib figure so the web UI
    can render it client-side. Raises ValueError on any failure/empty result - callers
    decide how to surface that (api_server.py maps it to a 404).
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
    except Exception as e:
        raise ValueError(f"yfinance download failed for {ticker}: {e}") from e

    if df.empty:
        raise ValueError(f"No chart data returned for {ticker}")

    close = df["Close"]
    # Recent yfinance versions return MultiIndex columns (Price, Ticker) even for a
    # single symbol, so df["Close"] is a one-column DataFrame, not a Series.
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    return [
        {"timestamp": ts.isoformat(), "close": round(float(value), 4)}
        for ts, value in close.items()
        if pd.notna(value)
    ]
