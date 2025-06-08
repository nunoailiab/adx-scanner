import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

def show_ticker_info(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False)

    if df.empty or len(df) < 60:
        print(f"❌ Not enough data for '{ticker}'\n")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Technical Indicators
    df.ta.ema(length=10, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.sma(length=50, append=True)
    adx_df = ta.adx(high=df["High"], low=df["Low"], close=df["Close"], length=14)
    df = pd.concat([df, adx_df], axis=1)

    # Daily Range & Color Tag
    df["Range"] = df["High"] - df["Low"]
    df["Color"] = df.apply(lambda row: "🟢 Green" if row["Close"] > row["Open"] else "🔴 Red", axis=1)

    # % Returns
    today = df.index[-1]
    close_today = df["Close"].iloc[-1]

    def calc_return(days):
        past_date = today - timedelta(days=days)
        past_data = df[df.index <= past_date]
        if past_data.empty:
            return "N/A"
        past_close = past_data["Close"].iloc[-1]
        return round(((close_today - past_close) / past_close) * 100, 2)

    return_7d = calc_return(7)
    return_30d = calc_return(30)
    return_90d = calc_return(90)

    last_row = df.iloc[-1]
    ema20 = last_row.get("EMA_20", float("nan"))
    sma50 = last_row.get("SMA_50", float("nan"))
    adx = last_row.get("ADX_14", float("nan"))
    plus_di = last_row.get("DMP_14", float("nan"))
    minus_di = last_row.get("DMN_14", float("nan"))

    below_ema20 = close_today < ema20
    below_sma50 = close_today < sma50

    # --- Output --- #
    print(f"\n📊 Technical Indicators for {ticker.upper()}")
    print("----------------------------------------")
    print(f"Current Price:   {round(close_today, 2)}")
    print(f"EMA 10:          {round(last_row['EMA_10'], 2)}")
    print(f"EMA 20:          {round(ema20, 2)}")
    print(f"SMA 50:          {round(sma50, 2)}")
    print(f"ADX (14):        {round(adx, 2)}")
    print(f"+DI (14):        {round(plus_di, 2)}")
    print(f"-DI (14):        {round(minus_di, 2)}")

    print("\n📈 Returns:")
    print(f"1W  Change:      {return_7d}%")
    print(f"1M  Change:      {return_30d}%")
    print(f"3M  Change:      {return_90d}%")

    print("\n🔍 Price Flags:")
    print(f"⬇️  Below 20 EMA: {'Yes' if below_ema20 else 'No'}")
    print(f"⬇️  Below 50 SMA: {'Yes' if below_sma50 else 'No'}")

    print("\n🕵️‍♂️ Last 10 Trading Days:")
    print("--------------------------------------------------------------")
    last_10 = df.tail(10)[["Open", "Close", "High", "Low", "Range", "Volume", "Color"]]
    print(last_10.round(2).to_string(index=True))


# === Interactive Loop === #
print("📘 Type 'exit' to quit.")
while True:
    ticker = input("\nEnter stock ticker: ").strip()
    if ticker.lower() == "exit":
        break
    if not ticker:
        continue
    show_ticker_info(ticker)
