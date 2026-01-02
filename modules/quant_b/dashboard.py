import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf

# [Quant B] Function to calculate portfolio performance & metrics
def calculate_portfolio(weights, data):
    # 1. Normalize weights to sum to 1 (Safety check)
    weights = np.array(weights)
    if weights.sum() == 0: # Prevent division by zero
        weights = np.array([1/len(weights)] * len(weights))
    else:
        weights /= weights.sum()
    
    # 2. Calculate daily returns
    returns = data.pct_change().dropna()
    
    # 3. Portfolio return (Daily)
    port_daily_ret = returns.dot(weights)
    
    # 4. Cumulative return (Base 100)
    cumulative_return = (1 + port_daily_ret).cumprod() * 100
    
    # 5. Metrics Calculation
    # [Correction] Sharpe Ratio requires Annualized Return, not Cumulative Total Return
    mean_daily_return = port_daily_ret.mean()
    annual_return = mean_daily_return * 252 # Annualized Expected Return
    
    annual_volatility = port_daily_ret.std() * np.sqrt(252)
    
    # Risk-free rate assumed 2% (0.02)
    sharpe_ratio = (annual_return - 0.02) / annual_volatility if annual_volatility != 0 else 0
    
    total_return_pct = (cumulative_return.iloc[-1] / 100) - 1

    #  Diversification Effect
    # Formula: Weighted Avg Volatility of Assets - Portfolio Volatility
    asset_volatilities = returns.std() * np.sqrt(252)
    weighted_avg_vol = np.dot(weights, asset_volatilities)
    diversification_effect = weighted_avg_vol - annual_volatility

    # Correlation Matrix
    correlation_matrix = returns.corr()
    
    return {
        "cumulative_return": cumulative_return,
        "total_return_pct": total_return_pct,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "diversification_effect": diversification_effect,
        "correlation_matrix": correlation_matrix
    }

def display_quant_b_dashboard():
    st.title("Quant B: Multivariate & Portfolio Simulation")
    
    # --- Sidebar Configuration ---
    st.sidebar.header("1. Asset Selection")
    
    # Default Tickers
    available_tickers = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "NVDA"]
    selected_tickers = st.sidebar.multiselect(
        "Select Assets (Min 3)", 
        available_tickers, 
        default=["AAPL", "GOOGL", "MSFT"]
    )
    
    if len(selected_tickers) < 3:
        st.warning("Please select at least 3 assets as per module requirements.")
        return

    # --- Weight Selection ---
    st.sidebar.header("2. Strategy Parameters")
    st.sidebar.subheader("Target Allocation")
    
    input_weights = []
    # Using columns for cleaner UI in sidebar
    for ticker in selected_tickers:
        w = st.sidebar.slider(f"Weight: {ticker}", 0.0, 1.0, 1.0/len(selected_tickers), 0.05)
        input_weights.append(w)
    
    # Show current total weight
    total_weight = sum(input_weights)
    if not (0.99 <= total_weight <= 1.01):
        st.sidebar.warning(f"Current Total Weight: {total_weight:.2f}. Will be normalized to 1.0 automatically.")

    # --- Fetch Data ---
    @st.cache_data
    def get_data(tickers):
        # Fetching 2 years of data
        data = yf.download(tickers, period="2y")['Adj Close']
        return data

    try:
        data = get_data(selected_tickers)
        
        # Handle case where only 1 ticker is returned (Series -> DF)
        if isinstance(data, pd.Series):
            data = data.to_frame()
            
        # Drop missing columns if download failed for some
        data = data.dropna(axis=1, how='all').dropna()

        if data.empty:
            st.error("No data found. Please check tickers.")
            return

        # --- Calculate Logic ---
        results = calculate_portfolio(input_weights, data)
        
        # --- Display Metrics ---
        st.subheader("Portfolio Performance Metrics")
        
        # Row 1: Key Performance Indicators
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Annual Return (Exp)", f"{results['annual_return']:.2%}")
        col2.metric("Annual Volatility", f"{results['annual_volatility']:.2%}")
        col3.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
        col4.metric("Diversification Effect", f"{results['diversification_effect']:.2%}", 
                    help="Difference between Weighted Avg Asset Volatility and Portfolio Volatility")
        
        st.markdown("---")

        # --- Display Charts ---
        
        # 1. Main Chart: Cumulative Performance
        st.subheader("Historical Performance (Base 100)")
        
        # Combine Portfolio with Individual Assets for comparison
        chart_data = data.copy()
        # Normalize individual assets to start at 100
        chart_data = (chart_data / chart_data.iloc[0]) * 100
        chart_data['PORTFOLIO'] = results['cumulative_return']
        
        st.line_chart(chart_data)
        
        # 2. Correlation Matrix (Required Feature)
        st.subheader("Asset Correlation Matrix")
        corr_matrix = results['correlation_matrix']
        
        # Using Plotly for better heatmap visualization
        fig_corr = px.imshow(
            corr_matrix, 
            text_auto=True, 
            aspect="auto", 
            color_continuous_scale='RdBu_r', 
            zmin=-1, zmax=1
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
    except Exception as e:
        st.error(f"An error occurred during calculation: {e}")

# Entry point for testing independently
if __name__ == "__main__":
    display_quant_b_dashboard()
