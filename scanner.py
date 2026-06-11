import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import os

ADX_LEVEL = 20

HISTORY_FILE = "history.csv"


def get_signal(df):
    df = df.dropna()

    if len(df) < 50:
        return None

    macd = ta.trend.MACD(df["Close"], 12, 26, 9)
    macd_line = macd.macd()

    adx = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"], 14)

    prev_macd = macd_line.iloc[-2]
    curr_macd = macd_line.iloc[-1]

    adx_val = adx.adx().iloc[-1]
    plus = adx.adx_pos().iloc[-1]
    minus = adx.adx_neg().iloc[-1]

    if prev_macd < 0 and curr_macd > 0 and adx_val > ADX_LEVEL and plus > minus:
        return "BUY"

    if prev_macd > 0 and curr_macd < 0 and adx_val > ADX_LEVEL and minus > plus:
        return "SELL"

    return None


def load_universe():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    base = df["Symbol"].tolist()
    return (base * 4)[:2000]


def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    else:
        return pd.DataFrame(columns=["date", "ticker", "signal"])


def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)


def run():
    print("START")

    tickers = load_universe()
    history = load_history()

    today = datetime.now().strftime("%Y-%m-%d")

    new_rows = []

    for i, t in enumerate(tickers):

        try:
            df = yf.download(t, period="6mo", interval="1d", progress=False)

            if df is None or df.empty:
                continue

            sig = get_signal(df)

            if sig in ["BUY", "SELL"]:
                new_rows.append([today, t, sig])

        except:
            continue

        if i % 100 == 0:
            print("scanned:", i)

    # 🔥 DOPIS DO HISTORII
    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=["date", "ticker", "signal"])
        history = pd.concat([history, new_df], ignore_index=True)

    save_history(history)

    print("DONE")
    print("ROWS ADDED:", len(new_rows))


if __name__ == "__main__":
    run()
