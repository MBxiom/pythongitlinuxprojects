import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. Data Loading Function 
def load_data(ticker, period="2y", interval="1d"):
quant-a
   
    data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
    

    data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)

main
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    data.dropna(inplace=True)
    return data

# 2. Strategy Logic
def apply_strategy(df, strategy_type, params):
    signals = pd.DataFrame(index=df.index)
    signals['Signal'] = 0.0

    close_price = df['Close']
    
    if strategy_type == "SMA Crossover":
        short_window = params['short_window']
        long_window = params['long_window']
        signals['Short_MA'] = close_price.rolling(window=short_window).mean()
        signals['Long_MA'] = close_price.rolling(window=long_window).mean()
        signals['Signal'][short_window:] = np.where(
            signals['Short_MA'][short_window:] > signals['Long_MA'][short_window:], 1.0, 0.0
        )

    elif strategy_type == "Momentum":
        window = params['momentum_window']
        signals['MA'] = close_price.rolling(window=window).mean()
        signals['Signal'][window:] = np.where(
            close_price[window:] > signals['MA'][window:], 1.0, 0.0
        )
    return signals

# 3. Machine Learning: Linear Regression
def predict_next_day(df):
    df_ml = df.copy()
    
    close_col = df_ml['Close']
    
    for i in range(1, 6):
        df_ml[f'Lag_{i}'] = close_col.shift(i)
    
    df_ml['Target'] = close_col.shift(-1)
    df_ml.dropna(inplace=True)
    
    X = df_ml[[f'Lag_{i}' for i in range(1, 6)]]
    y = df_ml['Target']
    
    model = LinearRegression()
    model.fit(X, y)
    
    recent_data = close_col.tail(5).values[::-1].reshape(1, -1)
    prediction = model.predict(recent_data)[0]
    
    return float(prediction)

# 4. Metrics Calculation
def calculate_metrics(daily_returns):
    strategy_mean = daily_returns.mean() * 252
    strategy_std = daily_returns.std() * np.sqrt(252)
    sharpe = strategy_mean / strategy_std if strategy_std != 0 else 0
    
    cum_ret = (1 + daily_returns).cumprod()
    peak = cum_ret.cummax()
    mdd = ((cum_ret - peak) / peak).min()
    return sharpe, mdd

# 5. Main UI Rendering
def render_quant_a():
    st.title("Quant A: Analysis & AI Prediction")
    st.markdown("---")

    st.sidebar.header("Configuration")
    ticker = st.sidebar.text_input("Ticker Symbol", value="EURKRW=X")
    strategy_type = st.sidebar.selectbox("Select Strategy", ["SMA Crossover", "Momentum"])
    
    params = {}
    if strategy_type == "SMA Crossover":
        params['short_window'] = st.sidebar.slider("Short Window", 5, 50, 20)
        params['long_window'] = st.sidebar.slider("Long Window", 50, 200, 50)
    elif strategy_type == "Momentum":
        params['momentum_window'] = st.sidebar.slider("Lookback Window", 10, 200, 60)
    
    show_ml = st.sidebar.checkbox("Show AI Prediction (Bonus)", value=True)

    if st.sidebar.button("Run Analysis"):
        with st.spinner(f"Processing data for {ticker}..."):
            try:
                df = load_data(ticker)
                if df.empty:
                    st.error("No data found.")
                    return
            except Exception as e:
                st.error(f"Error: {e}")
                return

            signals = apply_strategy(df, strategy_type, params)
            
            # Returns Calculation
            market_return = df['Close'].pct_change()
            strategy_return = market_return * signals['Signal'].shift(1)
            
            cum_market = (1 + market_return).cumprod()
            cum_strategy = (1 + strategy_return).cumprod()

            sharpe, mdd = calculate_metrics(strategy_return)
            
            st.subheader("Strategy Performance")
            col1, col2 = st.columns(2)
            col1.metric("Sharpe Ratio", f"{sharpe:.2f}")
            col2.metric("Max Drawdown", f"{mdd:.2%}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=cum_market, mode='lines', name='Buy & Hold', line=dict(color='gray', dash='dash')))
            fig.add_trace(go.Scatter(x=df.index, y=cum_strategy, mode='lines', name='Strategy', line=dict(color='blue', width=2)))
            fig.update_layout(title=f"Performance: {ticker}", template="plotly_white", height=500)
            st.plotly_chart(fig, use_container_width=True)

            if show_ml:
                st.markdown("---")
                st.subheader("AI Price Prediction (Bonus Feature)")
                
                try:
                    predicted_price = predict_next_day(df)
                    
                    raw_current = df['Close'].iloc[-1]
                    if hasattr(raw_current, 'item'):
                        current_price = raw_current.item()
                    else:
                        current_price = float(raw_current)
                        
                except Exception as ml_error:
                    st.error(f"Calculation Error: {ml_error}")
                    return

                change_pct = ((predicted_price - current_price) / current_price) * 100
                
                c1, c2 = st.columns(2)
                c1.metric("Current Price", f"{current_price:.2f}")
                c2.metric("Predicted Next Day", f"{predicted_price:.2f}", f"{change_pct:.2f}%")
                
                if change_pct > 0:
                    st.success(f"AI Prediction: UPWARD trend (+{change_pct:.2f}%) 📈")
                else:
                    st.error(f"AI Prediction: DOWNWARD trend ({change_pct:.2f}%) 📉")

if __name__ == "__main__":
    render_quant_a()
