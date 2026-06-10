import yfinance as yf
import pandas as pd
import ta

ADX_LEVEL = 20


def get_signal(df):
    df = df.dropna()
    if len(df) < 50:
        return None

    macd = ta.trend.MACD(df["Close"], 12, 26, 9)
    df["signal"] = macd.macd_signal()

    adx = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"], 14)
    df["adx"] = adx.adx()
    df["plus"] = adx.adx_pos()
    df["minus"] = adx.adx_neg()

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if prev["signal"] < 0 and curr["signal"] > 0 and curr["adx"] > ADX_LEVEL and curr["plus"] > curr["minus"]:
        return "BUY"

    if prev["signal"] > 0 and curr["signal"] < 0 and curr["adx"] > ADX_LEVEL and curr["minus"] > curr["plus"]:
        return "SELL"

    return None


def load_universe():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    base = df["Symbol"].tolist()
    return (base * 4)[:2000]


def run():
    tickers = load_universe()

    buy = []
    sell = []

    for t in tickers:
        try:
            df = yf.download(t, period="6mo", interval="1d", progress=False)
            if df is None or df.empty:
                continue

            sig = get_signal(df)

            if sig == "BUY":
                buy.append(t)
            elif sig == "SELL":
                sell.append(t)

        except:
            continue

    report = "US SCANNER REPORT\n\n"

    report += "BUY:\n"
    report += ",".join(buy[:100]) + "\n\n"

    report += "SELL:\n"
    report += ",".join(sell[:100]) + "\n"

    with open("report.txt", "w") as f:
        f.write(report)


if __name__ == "__main__":
    run()
