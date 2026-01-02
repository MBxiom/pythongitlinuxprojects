import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

def run_quant_a():
    st.header("Quant A: Single Asset Analysis")
    st.markdown("### 💶 EUR/KRW Exchange Rate Analysis")
    st.info("Real-time analysis of Euro to Korean Won exchange rate.")

    # 1. Fetch Data (EURKRW=X)
    ticker = "EURKRW=X"
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365) # 1 Year data

    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        
        if not data.empty:
            # 2. Display Metrics
            # Handle multi-index columns if necessary (yfinance update)
            if isinstance(data.columns, pd.MultiIndex):
                close_price = data['Close'][ticker]
            else:
                close_price = data['Close']

            current_price = close_price.iloc[-1]
            prev_price = close_price.iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric("EUR/KRW Rate", f"₩{current_price:,.2f}", f"{change:,.2f} ({change_pct:.2f}%)")
            
            # 3. Chart
            st.write("#### Price Trend (1 Year)")
            st.line_chart(close_price)
            
            st.success("Data retrieved successfully from Yahoo Finance.")
        else:
            st.error("No data found. Please check your internet connection.")

    except Exception as e:
        st.error(f"An error occurred: {e}")