import streamlit as st
import sys
import os

# --- CORRECTION DU CHEMIN (PATH FIX) ---
# On ajoute le dossier racine du projet au chemin de recherche de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)
# ---------------------------------------

import plotly.express as px
from modules.quant_b.data_retrieval import get_multiple_data
from modules.quant_b.portfolio import simulate_portfolio

def display_quant_b_dashboard():
    st.header("💰 Gestion de Portefeuille (Quant B)")

    # 1. Contrôles Utilisateur
    st.sidebar.subheader("Paramètres du Portefeuille")
    default_tickers = "AAPL,GOOGL,TSLA,MSFT"
    tickers = st.sidebar.text_input("Actifs (séparés par virgule)", default_tickers).split(',')
    tickers = [t.strip().upper() for t in tickers]

    # 2. Récupération des données
    if st.sidebar.button("Lancer l'analyse"):
        try:
            with st.spinner('Téléchargement des données...'):
                df_prices = get_multiple_data(tickers)
            
            st.success("Données récupérées !")
            
            # 3. Poids égaux
            weights = {t: 1/len(tickers) for t in tickers}
            st.write(f"**Répartition (Equipondéré) :** {weights}")

            # 4. Calcul
            portfolio_val = simulate_portfolio(df_prices, weights)

            # 5. Graphique
            st.subheader("Performance : Portefeuille vs Actifs")
            df_normalized = (df_prices / df_prices.iloc[0]) * 100
            df_normalized['Portfolio'] = portfolio_val

            fig = px.line(df_normalized, title="Comparaison Base 100")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur : {e}")

if __name__ == "__main__":
    display_quant_b_dashboard()
