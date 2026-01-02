import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf

# [Quant B] Portfolio Calculation Function
def calculate_portfolio(weights, data):
    # 1. Normalize weights
    weights = np.array(weights)
    if weights.sum() == 0:
        weights = np.array([1/len(weights)] * len(weights))
    else:
        weights /= weights.sum()
    
    # 2. Daily Returns
    returns = data.pct_change().dropna()
    
    # 3. Portfolio Return (Daily)
    port_daily_ret = returns.dot(weights)
    
    # 4. Cumulative Return (Base 100)
    cumulative_return = (1 + port_daily_ret).cumprod() * 100
    
    # 5. Metrics (Corrected Logic)
    # Annualized Return & Volatility
    mean_daily_return = port_daily_ret.mean()
    annual_return = mean_daily_return * 252 
    annual_volatility = port_daily_ret.std() * np.sqrt(252)
    
    # Sharpe Ratio (Risk-free rate 2%)
    sharpe_ratio = (annual_return - 0.02) / annual_volatility if annual_volatility != 0 else 0
    
    # Diversification Effect
    asset_vols = returns.std() * np.sqrt(252)
    weighted_asset_vol = np.dot(weights, asset_vols)
    diversification_effect = weighted_asset_vol - annual_volatility

    # Correlation Matrix
    correlation_matrix = returns.corr()
    
    return {
        "cumulative_return": cumulative_return,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "diversification_effect": diversification_effect,
        "correlation_matrix": correlation_matrix
    }

# [Quant B] Main Display Function
def display_quant_b_dashboard():
    st.title("Quant B: Multivariate & Portfolio Simulation")
    
    # Sidebar
    st.sidebar.header("1. Asset Selection")
    tickers = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "NVDA"]
    selected_tickers = st.sidebar.multiselect("Select Assets (Min 3)", tickers, default=["AAPL", "GOOGL", "MSFT"])
    
    if len(selected_tickers) < 3:
        st.warning("Please select at least 3 assets.")
        return

    st.sidebar.header("2. Weights")
    weights = []
    for t in selected_tickers:
        weights.append(st.sidebar.slider(f"Weight: {t}", 0.0, 1.0, 1.0/len(selected_tickers), 0.05))

    # Data Fetching
    data = yf.download(selected_tickers, period="2y")['Adj Close']
    if isinstance(data, pd.Series): data = data.to_frame()
    data = data.dropna(axis=1, how='all').dropna()

    if not data.empty:
        # Calculate
        results = calculate_portfolio(weights, data)

        # Metrics
        st.subheader("Portfolio Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Exp Return (Ann)", f"{results['annual_return']:.2%}")
        c2.metric("Volatility (Ann)", f"{results['annual_volatility']:.2%}")
        c3.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
        c4.metric("Diversification", f"{results['diversification_effect']:.2%}")

        # Charts
        st.subheader("Historical Performance (Base 100)")
        chart_data = (data / data.iloc[0]) * 100
        chart_data['PORTFOLIO'] = results['cumulative_return']
        st.line_chart(chart_data)

        # Correlation Heatmap
        st.subheader("Correlation Matrix")
        fig = px.imshow(results['correlation_matrix'], text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)
