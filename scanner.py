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


def run():
    print("START")

    tickers = load_universe()

    results = {
        "BUY": [],
        "SELL": []
    }

    for i, t in enumerate(tickers):

        try:
            df = yf.download(t, period="6mo", interval="1d", progress=False)

            if df is None or df.empty:
                continue

            sig = get_signal(df)

            if sig == "BUY":
                results["BUY"].append(t)

            elif sig == "SELL":
                results["SELL"].append(t)

        except:
            continue

        if i % 100 == 0:
            print("progress:", i)

    print("DONE")

    # 🔥 DATE FILE NAME
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"report_{date_str}.txt"

    report = "US SCANNER REPORT\n\n"
    report += f"DATE: {date_str}\n\n"
    report += f"BUY: {len(results['BUY'])}\n"
    report += f"SELL: {len(results['SELL'])}\n\n"

    report += "BUY LIST:\n" + ",".join(results["BUY"][:100]) + "\n\n"
    report += "SELL LIST:\n" + ",".join(results["SELL"][:100])

    with open(filename, "w") as f:
        f.write(report)

    print("FILE CREATED:", filename)


if __name__ == "__main__":
    run()
