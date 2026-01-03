import yfinance as yf
import pandas as pd

def get_multiple_data(tickers):
    print(f" loading data for : {tickers}...")
    
    data = yf.download(tickers, period="5d", interval="5m", progress=False)
    
    if len(tickers) == 1:
        return data['Close'].to_frame() 
        
    return data['Close']
