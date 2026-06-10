import yfinance as yf
import pandas as pd
import ta

ADX_LEVEL = 20


def get_signal(df):
    try:
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

    except:
        return None

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
    report += "BUY:\n" + ",".join(buy[:100]) + "\n\n"
    report += "SELL:\n" + ",".join(sell[:100]) + "\n"

    # 🔥 GUARANTEE FILE EXISTS
    with open("report.txt", "w") as f:
        f.write(report)

    print("FILE CREATED")


if __name__ == "__main__":
    run()
