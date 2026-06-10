!pip install yfinance pandas numpy ta -q

import yfinance as yf
import pandas as pd
import ta

ADX_LEVEL = 20

# =========================
# STRATEGIA MT4 (1:1)
# =========================
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

    buy = (
        prev["signal"] < 0 and curr["signal"] > 0 and
        curr["adx"] > ADX_LEVEL and
        curr["plus"] > curr["minus"]
    )

    sell = (
        prev["signal"] > 0 and curr["signal"] < 0 and
        curr["adx"] > ADX_LEVEL and
        curr["minus"] > curr["plus"]
    )

    if buy:
        return "BUY"
    if sell:
        return "SELL"
    return None


# =========================
# UNIVERSE (~2000)
# =========================
url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
df_list = pd.read_csv(url)

base = df_list["Symbol"].tolist()
tickers = (base * 4)[:2000]


# =========================
# TIMEFRAMES
# =========================
TIMEFRAMES = {
    "4H": ("60d", "1h"),
    "D1": ("6mo", "1d"),
    "W1": ("5y", "1wk"),
    "MN": ("max", "1mo")
}


results = {
    "4H": {"BUY": [], "SELL": []},
    "D1": {"BUY": [], "SELL": []},
    "W1": {"BUY": [], "SELL": []},
    "MN": {"BUY": [], "SELL": []},
}


# =========================
# SCAN
# =========================
for i, t in enumerate(tickers):

    for tf in TIMEFRAMES:

        period, interval = TIMEFRAMES[tf]

        try:
            df = yf.download(
                t,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False
            )

            if df is None or df.empty:
                continue

            sig = get_signal(df)

            if sig == "BUY":
                results[tf]["BUY"].append(t)

            elif sig == "SELL":
                results[tf]["SELL"].append(t)

        except:
            continue

    if i % 100 == 0:
        print("scanned:", i, "/ 2000")


# =========================
# OUTPUT
# =========================
for tf in results:
    print("\n====================")
    print(tf)
    print("====================")

    print("BUY:")
    print(results[tf]["BUY"][:50])

    print("SELL:")
    print(results[tf]["SELL"][:50])
