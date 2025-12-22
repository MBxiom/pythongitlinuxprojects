import yfinance as yf
import pandas as pd

def get_multiple_data(tickers):
    print(f" chargement des données pour : {tickers}...")
    
    # chargement des données sur 5jours toutes les 5 minutes 
    data = yf.download(tickers, period="5d", interval="5m", progress=False)
    
    #que la colonne 'Close' : Prix de fermeture
    # Si un seul ticker est demandé, yfinance change le format on pallie ça :
    if len(tickers) == 1:
        return data['Close'].to_frame() 
        
    return data['Close']
