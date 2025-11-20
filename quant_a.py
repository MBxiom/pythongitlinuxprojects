import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. Data Loading Function
# ==========================================
def load_data(ticker, period="5y", interval="1d"):
    """
    Fetches historical market data from Yahoo Finance.
    Args:
        ticker (str): Symbol (e.g., 'EURKRW=X').
        period (str): Time period to download (e.g., '1y', '5y', 'max').
        interval (str): Data interval (e.g., '1d' for daily, '1h' for hourly).
    """
    # Using 'auto_adjust=True' to get Adjusted Close directly if needed
    data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
    
    # Drop rows with missing values to prevent calculation errors
    data.dropna(inplace=True)
    return data

# ==========================================
# 2. Strategy Logic
# ==========================================
def apply_strategy(df, strategy_type, params):
    """
    Applies a selected trading strategy to the dataframe.
    Returns a DataFrame with 'Signal' (1=Buy/Hold, 0=Cash/Sell).
    """
    signals = pd.DataFrame(index=df.index)
    signals['Signal'] = 0.0

    # --- Strategy 1: Simple Moving Average (SMA) Crossover ---
    if strategy_type == "SMA Crossover":
        short_window = params['short_window']
        long_window = params['long_window']

        # Calculate Indicators
        signals['Short_MA'] = df['Close'].rolling(window=short_window).mean()
        signals['Long_MA'] = df['Close'].rolling(window=long_window).mean()

        # Generate Signal: 1 when Short MA > Long MA
        signals['Signal'][short_window:] = np.where(
            signals['Short_MA'][short_window:] > signals['Long_MA'][short_window:], 1.0, 0.0
        )

    # --- Strategy 2: Momentum (Price vs Moving Average) ---
    elif strategy_type == "Momentum":
        window = params['momentum_window']
        
        # Calculate Indicator
        signals['MA'] = df['Close'].rolling(window=window).mean()
        
        # Generate Signal: 1 when Price > MA
        signals['Signal'][window:] = np.where(
            df['Close'][window:] > signals['MA'][window:], 1.0, 0.0
        )

    return signals

# ==========================================
# 3. Metrics Calculation
# ==========================================
def calculate_metrics(daily_returns):
    """
    Calculates Sharpe Ratio and Max Drawdown.
    """
    # Annualized Return & Std Dev (252 trading days)
    strategy_mean = daily_returns.mean() * 252
    strategy_std = daily_returns.std() * np.sqrt(252)
    
    # Sharpe Ratio (Risk-free rate = 0)
    sharpe = strategy_mean / strategy_std if strategy_std != 0 else 0
    
    # Max Drawdown
    cum_ret = (1 + daily_returns).cumprod()
    peak = cum_ret.cummax()
    drawdown = (cum_ret - peak) / peak
    mdd = drawdown.min()
    
    return sharpe, mdd

# ==========================================
# 4. Main UI Rendering (Streamlit)
# ==========================================
def render_quant_a():
    st.title("Quant A: Single Asset Analysis")
    st.markdown("---")

    # --- Sidebar: Controls ---
    st.sidebar.header("Configuration")
    
    # A. Asset Selection
    ticker = st.sidebar.text_input("Ticker Symbol", value="EURKRW=X")
    st.sidebar.caption("Example: EURKRW=X, AAPL, BTC-USD")

    # B. Strategy Selection
    strategy_type = st.sidebar.selectbox(
        "Select Strategy", 
        ["SMA Crossover", "Momentum"]
    )

    # C. Strategy Parameters (Dynamic based on selection)
    params = {}
    if strategy_type == "SMA Crossover":
        st.sidebar.subheader("SMA Parameters")
        params['short_window'] = st.sidebar.slider("Short Window", 5, 50, 20)
        params['long_window'] = st.sidebar.slider("Long Window", 50, 200, 50)
    elif strategy_type == "Momentum":
        st.sidebar.subheader("Momentum Parameters")
        params['momentum_window'] = st.sidebar.slider("Lookback Window", 10, 200, 60)

    # --- Main Execution ---
    if st.sidebar.button("Run Analysis"):
        with st.spinner(f"Downloading data for {ticker}..."):
            # 1. Load Data
            try:
                df = load_data(ticker)
                if df.empty:
                    st.error("No data found. Please check the ticker.")
                    return
            except Exception as e:
                st.error(f"Error loading data: {e}")
                return

            # 2. Apply Strategy
            signals = apply_strategy(df, strategy_type, params)

            # 3. Calculate Returns
            # Market Return (Buy & Hold)
            df['Market_Return'] = df['Close'].pct_change()
            
            # Strategy Return (Shifted signal to avoid look-ahead bias)
            df['Strategy_Return'] = df['Market_Return'] * signals['Signal'].shift(1)

            # Cumulative Returns (for Chart)
            df['Cum_Market'] = (1 + df['Market_Return']).cumprod()
            df['Cum_Strategy'] = (1 + df['Strategy_Return']).cumprod()

            # 4. Calculate Metrics
            sharpe, mdd = calculate_metrics(df['Strategy_Return'])
            bh_sharpe, bh_mdd = calculate_metrics(df['Market_Return'])

            # --- Dashboard Layout ---
            
            # Top: Key Metrics
            st.subheader(f"Performance: {strategy_type} vs Buy & Hold")
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Strategy Sharpe", f"{sharpe:.2f}")
            col2.metric("Strategy MDD", f"{mdd:.2%}")
            col3.metric("Benchmark Sharpe", f"{bh_sharpe:.2f}")
            col4.metric("Benchmark MDD", f"{bh_mdd:.2%}")

            # Middle: Interactive Chart
            st.subheader("Equity Curve Comparison")
            fig = go.Figure()
            
            # Benchmark Line
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Cum_Market'], 
                mode='lines', name='Buy & Hold (Benchmark)',
                line=dict(color='gray', dash='dash')
            ))
            
            # Strategy Line
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Cum_Strategy'], 
                mode='lines', name=f'Strategy ({strategy_type})',
                line=dict(color='blue', width=2)
            ))

            fig.update_layout(
                title=f"Cumulative Returns: {ticker}",
                xaxis_title="Date",
                yaxis_title="Growth of $1 Investment",
                template="plotly_white",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Bottom: Data Table
            with st.expander("View Recent Data"):
                st.dataframe(df.tail(10))

# This allows running this file independently for testing
if __name__ == "__main__":
    render_quant_a()