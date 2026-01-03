import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------
# 1. Helper Functions (Strategy & Metrics)
# ---------------------------------------------------------
def calculate_metrics(daily_returns):
    """Calculate Sharpe Ratio and Max Drawdown"""
    mean_ret = daily_returns.mean()
    std_dev = daily_returns.std()
    
    if std_dev == 0:
        sharpe = 0
    else:
        sharpe = (mean_ret / std_dev) * np.sqrt(252)
    
    cumulative = (1 + daily_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    
    return sharpe, max_drawdown

def run_ml_prediction(df, days_ahead=30):
    """Simple Linear Regression for Prediction (Bonus Feature)"""
    df_pred = df.copy()
    df_pred['Numbers'] = range(len(df_pred))
    
    X = df_pred[['Numbers']]
    y = df_pred['Close']
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_idx = df_pred['Numbers'].iloc[-1]
    future_X = np.array(range(last_idx + 1, last_idx + 1 + days_ahead)).reshape(-1, 1)
    future_pred = model.predict(future_X)
    
    residuals = y - model.predict(X)
    std_resid = residuals.std()
    
    return future_pred, std_resid

# ---------------------------------------------------------
# 2. Main Quant A Function
# ---------------------------------------------------------
def run_quant_a():
    st.header("Quant A: Single Asset Analysis & AI Prediction")
    
    # --- Sidebar Controls ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quant A Settings")
    
    # 1. Asset Selection
    tickers = {
        "Euro / Korean Won": "EURKRW=X",
        "Gold": "GC=F",
        "S&P 500": "^GSPC",
        "Bitcoin": "BTC-USD",
        "Apple": "AAPL"
    }
    
    selected_name = st.sidebar.selectbox("Select Asset", list(tickers.keys()))
    ticker = tickers[selected_name]
    
    # 2. Strategy Parameters
    st.sidebar.markdown("**Strategy Parameters**")
    short_window = st.sidebar.slider("Short MA (Days)", 5, 50, 20)
    long_window = st.sidebar.slider("Long MA (Days)", 50, 200, 100)
    
    # --- Data Fetching ---
    @st.cache_data
    def get_data(symbol):
        try:
            df = yf.download(symbol, period="2y")
            
            # [Fix 1] Flatten MultiIndex columns (handling yfinance update)
            if isinstance(df.columns, pd.MultiIndex):
                # Try to find 'Close' in levels or just drop level 1
                try:
                    df = df.xs('Close', axis=1, level=0, drop_level=True)
                    # If xs returns a Series (single ticker), convert to DataFrame
                    if isinstance(df, pd.Series):
                        df = df.to_frame(name='Close')
                    else:
                        # If multiple columns remain, we might need to be specific, but for single ticker:
                        df.columns = ['Close'] 
                except:
                    # Fallback: just use level 0
                    df.columns = df.columns.get_level_values(0)

            # Standardize column names
            if 'Close' in df.columns:
                return df[['Close']]
            elif 'Adj Close' in df.columns:
                 return df[['Adj Close']].rename(columns={'Adj Close': 'Close'})
            else:
                return pd.DataFrame()
        except:
            return pd.DataFrame()

    data = get_data(ticker)
    
    if data.empty:
        st.error("Error fetching data. Try another asset.")
        return

    data = data.dropna()
    
    # --- Strategy Logic ---
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    
    data['Signal'] = 0.0
    # Use .iloc to safely set values
    data.iloc[short_window:, data.columns.get_loc('Signal')] = np.where(
        data['Short_MA'][short_window:] > data['Long_MA'][short_window:], 1.0, 0.0
    )
    data['Position'] = data['Signal'].shift(1)
    
    data['Market_Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Market_Returns'] * data['Position']
    
    data['Market_Cum'] = (1 + data['Market_Returns']).cumprod() * 100
    data['Strategy_Cum'] = (1 + data['Strategy_Returns']).cumprod() * 100
    
    # --- Metrics Calculation ---
    sharpe, mdd = calculate_metrics(data['Strategy_Returns'])
    
    # [Fix 2] Robust Scalar Extraction (The Safety Lock)
    # Extracts the value safely even if it's wrapped in a Series or DataFrame
    try:
        last_close = data['Close'].iloc[-1]
        if isinstance(last_close, pd.Series):
            last_close = last_close.iloc[0]
        current_price = float(last_close)

        last_return = data['Strategy_Cum'].iloc[-1]
        if isinstance(last_return, pd.Series):
            last_return = last_return.iloc[0]
        total_return = float(last_return - 100)
    except:
        current_price = 0.0
        total_return = 0.0
    
    # --- Dashboard Layout ---
    st.markdown("### 1. Asset & Strategy Performance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"{current_price:,.2f}")
    col2.metric("Total Return (Strat)", f"{total_return:.2f}%")
    col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
    col4.metric("Max Drawdown", f"{mdd:.2%}")
    
    st.markdown("---")
    
    st.markdown("### 2. Backtest Result: Buy-and-Hold vs Strategy")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Market_Cum'], mode='lines', name='Buy & Hold', line=dict(color='gray', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Strategy_Cum'], mode='lines', name='SMA Strategy', line=dict(color='blue', width=2)))
    fig.update_layout(title="Wealth Curve (Base 100)", xaxis_title="Date", yaxis_title="Portfolio Value")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    st.markdown("### 3. AI Price Prediction (Linear Regression)")
    if st.checkbox("Show Prediction Model"):
        days_forecast = 30
        pred_prices, std_dev = run_ml_prediction(data[['Close']], days_forecast)
        
        last_date = data.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_forecast)
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=data.index[-90:], y=data['Close'][-90:], name='Historical', line=dict(color='black')))
        fig_pred.add_trace(go.Scatter(x=future_dates, y=pred_prices, name='Prediction', line=dict(color='red', dash='dash')))
        
        upper_bound = pred_prices + (1.96 * std_dev)
        lower_bound = pred_prices - (1.96 * std_dev)
        
        fig_pred.add_trace(go.Scatter(
            x=np.concatenate([future_dates, future_dates[::-1]]),
            y=np.concatenate([upper_bound, lower_bound[::-1]]),
            fill='toself', fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Conf. Interval'
        ))
        fig_pred.update_layout(title=f"Price Forecast (Next {days_forecast} Days)")
        st.plotly_chart(fig_pred, use_container_width=True)
        st.info("Note: Simple Linear Regression model (Bonus Feature).")
