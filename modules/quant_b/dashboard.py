import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf

# ---------------------------------------------------------
# 1. Calculation Logic Function
# ---------------------------------------------------------
def calculate_portfolio_metrics(weights, data):
    """
    Calculates portfolio performance metrics including Return, Volatility, 
    Sharpe Ratio, Diversification Effect, and Correlation Matrix.
    """
    # 1. Normalize Weights (Safety check to ensure sum is 1)
    weights = np.array(weights)
    if weights.sum() == 0:
        weights = np.array([1/len(weights)] * len(weights))
    else:
        weights /= weights.sum()
    
    # 2. Calculate Daily Returns
    returns = data.pct_change().dropna()
    
    # 3. Calculate Portfolio Daily Return
    port_daily_ret = returns.dot(weights)
    
    # 4. Calculate Cumulative Return (Base 100)
    cumulative_return = (1 + port_daily_ret).cumprod() * 100
    
    # 5. Calculate Metrics
    # Annualized Expected Return
    mean_daily_return = port_daily_ret.mean()
    annual_return = mean_daily_return * 252 
    
    # Annualized Volatility
    annual_volatility = port_daily_ret.std() * np.sqrt(252)
    
    # Sharpe Ratio (Assuming Risk-free rate = 2%)
    sharpe_ratio = (annual_return - 0.02) / annual_volatility if annual_volatility != 0 else 0
    
    # Diversification Effect (Required Feature)
    # Formula: (Weighted Avg of Individual Volatilities) - (Portfolio Volatility)
    asset_vols = returns.std() * np.sqrt(252)
    weighted_asset_vol = np.dot(weights, asset_vols)
    diversification_effect = weighted_asset_vol - annual_volatility

    # Correlation Matrix (Required Feature)
    correlation_matrix = returns.corr()
    
    return {
        "cumulative_return": cumulative_return,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "diversification_effect": diversification_effect,
        "correlation_matrix": correlation_matrix
    }

# ---------------------------------------------------------
# 2. Main Display Function (Called by main.py)
# ---------------------------------------------------------
def display_quant_b_dashboard():
    """
    Renders the Quant B dashboard in Streamlit.
    """
    st.header("Quant B: Portfolio Management & Optimization")
    
    # --- Sidebar Settings (Quant B Specific) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quant B Settings")
    
    # 1. Asset Selection
    available_tickers = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "NVDA", "SPY"]
    selected_tickers = st.sidebar.multiselect(
        "Select Assets (Min 3)", 
        available_tickers, 
        default=["AAPL", "GOOGL", "MSFT"]
    )
    
    # Validation: Ensure at least 3 assets are selected
    if len(selected_tickers) < 3:
        st.warning("Please select at least 3 assets to proceed.")
        return

    # 2. Weight Allocation
    st.sidebar.markdown("**Portfolio Weights**")
    weights = []
    for ticker in selected_tickers:
        val = st.sidebar.slider(f"Weight: {ticker}", 0.0, 1.0, 1.0/len(selected_tickers), 0.05)
        weights.append(val)

    # --- Data Fetching ---
    @st.cache_data
    def get_data(tickers):
        try:
            # Download data using yfinance
            df = yf.download(tickers, period="2y")['Adj Close']
            # Ensure format is DataFrame even for single asset (edge case handling)
            if isinstance(df, pd.Series): 
                df = df.to_frame()
            # Drop columns with all NaNs and then drop rows with NaNs
            return df.dropna(axis=1, how='all').dropna()
        except Exception as e:
            return pd.DataFrame()

    data = get_data(selected_tickers)

    # Check if data is valid
    if data.empty or len(data.columns) < len(selected_tickers):
        st.error("Error fetching data. Please check tickers or try again later.")
        return

    # --- Run Calculations ---
    results = calculate_portfolio_metrics(weights, data)

    # --- Dashboard Layout ---
    
    # [Section 1] Key Metrics
    st.markdown("### 1. Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Exp. Return (Ann)", f"{results['annual_return']:.2%}")
    col2.metric("Volatility (Ann)", f"{results['annual_volatility']:.2%}")
    col3.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
    col4.metric("Diversification Eff.", f"{results['diversification_effect']:.2%}", 
                help="Positive value indicates risk reduction due to diversification.")

    st.markdown("---")

    # [Section 2] Charts
    col_chart, col_corr = st.columns([2, 1])
    
    with col_chart:
        st.markdown("### 2. Cumulative Performance (Base 100)")
        # Normalize individual assets for comparison
        chart_df = (data / data.iloc[0]) * 100
        # Add Portfolio to the chart data
        chart_df['PORTFOLIO'] = results['cumulative_return']
        st.line_chart(chart_df)

    with col_corr:
        st.markdown("### 3. Correlation Matrix")
        # Use Plotly for Heatmap visualization
        fig = px.imshow(
            results['correlation_matrix'], 
            text_auto=True, 
            color_continuous_scale='RdBu_r', 
            zmin=-1, zmax=1,
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
