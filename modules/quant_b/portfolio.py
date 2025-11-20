import pandas as pd
import numpy as np

def simulate_portfolio(data, weights):
    """
    Simule l'évolution d'un portefeuille.
    Arguments:
        data (pd.DataFrame): Tableau des prix (celui que vous venez de télécharger)
        weights (dict): Répartition (ex: {'AAPL': 0.5, 'TSLA': 0.5})
    Retourne:
        pd.Series: La valeur du portefeuille au fil du temps (base 100)
    """
    # 1. Normaliser les prix (faire commencer toutes les actions à 1.0)
    # Cela permet de comparer Apple (200$) et Google (150$) sur la même base
    normalized_data = data / data.iloc[0]

    # 2. Préparer la liste des poids dans le même ordre que les colonnes
    weight_list = []
    for ticker in data.columns:
        weight_list.append(weights.get(ticker, 0)) # 0 si pas de poids défini

    # 3. Calculer la valeur pondérée (Produit matriciel)
    # Formule : (Prix_A * Poids_A) + (Prix_B * Poids_B) ...
    portfolio_value = normalized_data.dot(weight_list)

    # On multiplie par 100 pour dire "Si j'avais investi 100€ au début"
    return portfolio_value * 100
