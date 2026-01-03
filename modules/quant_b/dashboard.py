import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf


# the basic function

def calculate_portfolio_metrics(weights, data):
  
    #normalizing weirhts
    weights = np.array(weights)
    if weights.sum() == 0:
        weights = np.array([1/len(weights)] * len(weights))
    else:
        weights /= weights.sum()
    
   #daily returns
    returns = data.pct_change().dropna()
    
   #portfolio daily returns
    port_daily_ret = returns.dot(weights)
    
   #cumulative return base 100
    cumulative_return = (1 + port_daily_ret).cumprod() * 100
    
   #metrics
    #annualized expected returns
    mean_daily_return = port_daily_ret.mean()
    annual_return = mean_daily_return * 252 
    
    # Annualized Volatility
    annual_volatility = port_daily_ret.std() * np.sqrt(252)
    
    # sharpe ratio (2%)
    sharpe_ratio = (annual_return - 0.02) / annual_volatility if annual_volatility != 0 else 0
    
    # Diversification Effect (because its required)
    # Formula: (Weighted Avg of Individual Volatilities) - (Portfolio Volatility)
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

# main display function

def display_quant_b_dashboard():
   
    st.header("Portfolio Management and Optimization")
    
    # sidebar settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("Settings")
    
    #selecting asset
    available_tickers = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "NVDA", "SPY"]
    selected_tickers = st.sidebar.multiselect(
        "Select Assets (Min 3)", 
        available_tickers, 
        default=["AAPL", "GOOGL", "MSFT"]
    )
    
    # validation for 3 assets
    if len(selected_tickers) < 3:
        st.warning("Please select at least 3 assets to proceed.")
        return

    #allocating weights
    st.sidebar.markdown("**Portfolio weights**")
    weights = []
    for ticker in selected_tickers:
        val = st.sidebar.slider(f"Weight: {ticker}", 0.0, 1.0, 1.0/len(selected_tickers), 0.05)
        weights.append(val)

   # searching for data
    @st.cache_data
    def get_data(tickers):
        try:
            # On ajoute group_by='ticker' pour stabiliser le format
            # et threads=False pour éviter les conflits
            df = yf.download(tickers, period="2y", group_by='column', progress=False)
            
            # Gestion sécurisée : on cherche 'Adj Close' ou 'Close'
            target_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            
            if target_col in df.columns:
                df = df[target_col]
            
            # Ensure format is DataFrame
            if isinstance(df, pd.Series): 
                df = df.to_frame()
                
            return df.dropna(axis=1, how='all').dropna()
            
        except Exception as e:
            st.error(f"Erreur technique yfinance : {e}") # Affiche la vraie erreur pour comprendre
            return pd.DataFrame()

    data = get_data(selected_tickers)

    # Check if data is valid
    if data.empty or len(data.columns) < len(selected_tickers):
        st.error("Error fetching data. Please check tickers or try again later.")
        return

    results = calculate_portfolio_metrics(weights, data)

    
    # Key Metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Exp. Return (Ann)", f"{results['annual_return']:.2%}")
    col2.metric("Volatility (Ann)", f"{results['annual_volatility']:.2%}")
    col3.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
    col4.metric("Diversification Eff.", f"{results['diversification_effect']:.2%}", 
                help="Positive value indicates risk reduction due to diversification.")

    st.markdown("---")

    # Charts
    col_chart, col_corr = st.columns([2, 1])
    
    with col_chart:
        st.markdown("### Cumulative Performance (Base 100)")
        # Normalize individual assets for comparison
        chart_df = (data / data.iloc[0]) * 100
        # Add Portfolio to the chart data
        chart_df['PORTFOLIO'] = results['cumulative_return']
        st.line_chart(chart_df)

    with col_corr:
        st.markdown("Correlation Matrix")
        # Use Plotly for Heatmap visualization
        fig = px.imshow(
            results['correlation_matrix'], 
            text_auto=True, 
            color_continuous_scale='RdBu_r', 
            zmin=-1, zmax=1,
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Test Quant B")
    display_quant_b_dashboard()
