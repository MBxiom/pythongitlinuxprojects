import pandas as pd
import numpy as np

def simulate_portfolio(data, weights):
    
    # 1) normalisation des prix
    # pour comparer apple (200 euros et google 150 euros sur la même base) 
    normalized_data = data / data.iloc[0]

    # 2) Preparation de la liste des poids avec le même ordre que les colonnes
    weight_list = []
    for ticker in data.columns:
        weight_list.append(weights.get(ticker, 0)) # 0 si pas de poids défini

    # 3)calcul de la valeur pondérée avec un Produit matriciel
    
    portfolio_value = normalized_data.dot(weight_list)

    # On multiplie par 100 pour dire "Si j'avais investi 100€ au début"
    return portfolio_value * 100
