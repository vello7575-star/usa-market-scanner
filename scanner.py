# FORCE UPDATE
print("NEW VERSION ACTIVE")
print("START FILE EXECUTION")
print("🔥 VERSION FIX ACTIVE")

import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import os

ADX_LEVEL = 19
HISTORY_FILE = "history.csv"

# -------------------------
# TIMEFRAMES
# -------------------------
TIMEFRAMES = {
    "4h": ("60d", "1h"),   # approx 4h via 1h candles
    "1d": ("6mo", "1d"),
    "1w": ("5y", "1wk"),
    "1m": ("10y", "1mo")
}

# -------------------------
# SIGNAL LOGIC (UNCHANGED)
# -------------------------
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

# -------------------------
# UNIVERSE
# -------------------------
def load_universe():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    base = df["Symbol"].tolist()
    return (base * 4)[:2000]

# -------------------------
# HISTORY
# -------------------------
def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    else:
        return pd.DataFrame(columns=["date", "ticker", "signal", "timeframe"])

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

# -------------------------
# MAIN RUN
# -------------------------
def run():
    print("START")

    tickers = load_universe()
    history = load_history()

    today = datetime.now().strftime("%Y-%m-%d")

    new_rows = []

    for tf_name, (period, interval) in TIMEFRAMES.items():

        print("TIMEFRAME:", tf_name)

        for i, t in enumerate(tickers):

            try:
                df = yf.download(
                    t,
                    period=period,
                    interval=interval,
                    progress=False
                )

                if df is None or df.empty:
                    continue

                sig = get_signal(df)

                if sig in ["BUY", "SELL"]:
                    new_rows.append([today, t, sig, tf_name])

            except:
                continue

            if i % 100 == 0:
                print(tf_name, "scanned:", i)

    # -------------------------
    # SAVE
    # -------------------------
    if new_rows:
        new_df = pd.DataFrame(
            new_rows,
            columns=["date", "ticker", "signal", "timeframe"]
        )
        history = pd.concat([history, new_df], ignore_index=True)

    save_history(history)

    print("DONE")
    print("ROWS ADDED:", len(new_rows))


if __name__ == "__main__":
    run()

print("END FILE EXECUTION")
