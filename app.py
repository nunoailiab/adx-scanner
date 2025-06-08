import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

st.title("📈 Stock Technical Scanner")

ticker = st.text_input("Enter stock ticker", "AAPL").upper()

if ticker:
    df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False)

    if df.empty or len(df) < 60:
        st.error(f"❌ Not enough data for '{ticker}'")
    else:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Technical indicators
        df.ta.ema(length=10, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.sma(length=50, append=True)
        adx_df = ta.adx(high=df["High"], low=df["Low"], close=df["Close"], length=14)
        df = pd.concat([df, adx_df], axis=1)

        df["Range"] = df["High"] - df["Low"]
        df["Color"] = df.apply(lambda row: "🟢 Green" if row["Close"] > row["Open"] else "🔴 Red", axis=1)

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

        # --- Display --- #
        st.subheader(f"📊 {ticker} Technical Overview")
        st.write(f"**Current Price:** {round(close_today, 2)}")
        st.write(f"**EMA 10:** {round(last_row['EMA_10'], 2)}")
        st.write(f"**EMA 20:** {round(ema20, 2)}")
        st.write(f"**SMA 50:** {round(sma50, 2)}")
        st.write(f"**ADX (14):** {round(adx, 2)} | **+DI:** {round(plus_di, 2)} | **-DI:** {round(minus_di, 2)}")

        st.subheader("📈 Returns")
        st.write(f"**1W Change:** {return_7d}%")
        st.write(f"**1M Change:** {return_30d}%")
        st.write(f"**3M Change:** {return_90d}%")

        st.subheader("🔍 Price Flags")
        st.write(f"⬇️ Below 20 EMA: **{'Yes' if below_ema20 else 'No'}**")
        st.write(f"⬇️ Below 50 SMA: **{'Yes' if below_sma50 else 'No'}**")

        st.subheader("🕵️‍♂️ Last 10 Trading Days")
        st.dataframe(df.tail(10)[["Open", "Close", "High", "Low", "Range", "Volume", "Color"]].round(2))
