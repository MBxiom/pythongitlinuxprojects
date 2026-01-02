import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf

# Function to calculate portfolio performance
def calculate_portfolio(weights, data):
    # Normalize weights to sum to 1
    weights = np.array(weights)
    weights /= weights.sum()
    
    # Calculate daily returns
    returns = data.pct_change().dropna()
    
    # Portfolio return
    port_return = returns.dot(weights)
    
    # Cumulative return (Base 100)
    cumulative_return = (1 + port_return).cumprod() * 100
    
    # Metrics
    total_return = (cumulative_return.iloc[-1] / 100) - 1
    annual_volatility = port_return.std() * np.sqrt(252)
    sharpe_ratio = (total_return - 0.02) / annual_volatility # Assuming 2% risk-free rate
    
    return cumulative_return, total_return, annual_volatility, sharpe_ratio

def display_quant_b_dashboard():
    st.title("Multivariate Analysis & Portfolio Simulation")
    
    # Sidebar Configuration
    st.sidebar.header("Simulation Parameters")
    
    # Asset Selection
    st.sidebar.subheader("Select Assets")
    tickers = ["AAPL", "GOOGL", "TSLA", "MSFT"]
    selected_tickers = st.sidebar.multiselect("Symbols (Ticker)", tickers, default=tickers)
    
    if not selected_tickers:
        st.warning("Please select at least one asset.")
        return

    # Weight Selection
    st.sidebar.subheader("Target Allocation")
    weights = []
    for ticker in selected_tickers:
        weights.append(st.sidebar.slider(f"Weight: {ticker}", 0.0, 1.0, 1.0/len(selected_tickers)))
    
    # Fetch Data (Caching to speed up)
    @st.cache_data
    def get_data(tickers):
        data = yf.download(tickers, period="2y")['Close']
        return data

    try:
        data = get_data(selected_tickers)
        
        # Calculate Logic
        cum_ret, tot_ret, vol, sharpe = calculate_portfolio(weights, data)
        
        # Display Metrics
        st.write("### Portfolio Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Return", f"{tot_ret*100:.2f}%")
        col2.metric("Annual Volatility", f"{vol*100:.2f}%")
        col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
        
        # Display Chart
        st.write("### Historical Performance (Base 100)")
        
        # Combine Portfolio with Individual Assets for comparison
        chart_data = data.copy()
        # Normalize individual assets to 100
        chart_data = (chart_data / chart_data.iloc[0]) * 100
        chart_data['Portfolio'] = cum_ret
        
        st.line_chart(chart_data)
        
    except Exception as e:
        st.error(f"Error fetching data or calculating: {e}")
