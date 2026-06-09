import yfinance as yf
import pandas as pd
import ta
import smtplib
import os
from email.mime.text import MIMEText

ADX_LEVEL = 20


def get_signal(df):
    df = df.dropna()

    if len(df) < 50:
        return None

    macd = ta.trend.MACD(df["Close"], window_fast=12, window_slow=26, window_sign=9)
    df["signal"] = macd.macd_signal()

    adx = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"], window=14)
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


def send_email(text):
    msg = MIMEText(text)
    msg["Subject"] = "US SCANNER"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_USER"]

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
    server.send_message(msg)
    server.quit()


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

    report = "US SCANNER\n\n"
    report += "BUY:\n" + ",".join(buy[:50]) + "\n\n"
    report += "SELL:\n" + ",".join(sell[:50]) + "\n"

    send_email(report)


if __name__ == "__main__":
    run()
