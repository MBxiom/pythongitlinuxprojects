import yfinance as yf
import pandas as pd

def get_multiple_data(tickers):
    """
    Récupère les prix de fermeture (Close) pour une liste d'actifs.
    Arguments:
        tickers (list): Liste des symboles (ex: ['AAPL', 'GOOG'])
    Retourne:
        pd.DataFrame: Tableau des prix
    """
    print(f"📥 Téléchargement des données pour : {tickers}...")
    
    # Télécharger les données (période 5 jours, intervalle 5 minutes)
    data = yf.download(tickers, period="5d", interval="5m", progress=False)
    
    # On ne garde que la colonne 'Close' (Prix de fermeture)
    # Si un seul ticker est demandé, yfinance change le format, on sécurise ça :
    if len(tickers) == 1:
        return data['Close'].to_frame() # Force en tableau
        
    return data['Close']
