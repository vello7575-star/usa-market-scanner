import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import os

ADX_LEVEL = 20


def get_signal(df):
    df = df.dropna()

    if len(df) < 50:
        return None

    macd = ta.trend.MACD(df["Close"], 12, 26, 9)
    signal = macd.macd_signal()

    adx = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"], 14)

    prev_s = signal.iloc[-2]
    curr_s = signal.iloc[-1]

    adx_v = adx.adx().iloc[-1]
    plus = adx.adx_pos().iloc[-1]
    minus = adx.adx_neg().iloc[-1]

    if prev_s < 0 and curr_s > 0 and adx_v > ADX_LEVEL and plus > minus:
        return "BUY"

    if prev_s > 0 and curr_s < 0 and adx_v > ADX_LEVEL and minus > plus:
        return "SELL"

    return None


def load_universe():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    base = df["Symbol"].tolist()

    # stabilna wersja (bez crashy)
    return (base * 2)[:500]


def run():
    print("START SCAN")

    tickers = load_universe()

    buy = []
    sell = []

    for i, t in enumerate(tickers):

        try:
            df = yf.download(t, period="6mo", interval="1d", progress=False)

            if df is None or df.empty:
                continue

            sig = get_signal(df)

            if sig == "BUY":
                buy.append(t)
            elif sig == "SELL":
                sell.append(t)

        except Exception as e:
            print("ERROR:", t)
            continue

        if i % 100 == 0:
            print("progress:", i)

    print("SCAN DONE")

    date_str = datetime.now().strftime("%Y-%m-%d")

    report = ""
    report += "US SCANNER REPORT\n\n"
    report += "DATE: " + date_str + "\n\n"
    report += "BUY COUNT: " + str(len(buy)) + "\n"
    report += "SELL COUNT: " + str(len(sell)) + "\n\n"
    report += "BUY:\n" + ",".join(buy[:50]) + "\n\n"
    report += "SELL:\n" + ",".join(sell[:50]) + "\n"

    # 🔥 ABSOLUTNIE PEWNY ZAPIS
    file_path = os.path.join(os.getcwd(), "report.txt")

    with open(file_path, "w") as f:
        f.write(report)

    print("FILE WRITTEN:", file_path)
    print("EXISTS:", os.path.exists(file_path))
    print("DONE")


if __name__ == "__main__":
    run()
