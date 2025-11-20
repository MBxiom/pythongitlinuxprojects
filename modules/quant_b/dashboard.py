import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DU CHEMIN D'ACCÈS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)
# ---------------------------------------

from modules.quant_b.data_retrieval import get_multiple_data
from modules.quant_b.portfolio import simulate_portfolio

def display_quant_b_dashboard():
    st.set_page_config(page_title="Analyse de Portefeuille", layout="wide")
    st.title("Analyse Multivariée & Simulation de Portefeuille")

    # --- BARRE LATÉRALE : CONFIGURATION ---
    st.sidebar.header("Configuration")
    
    # 1. Sélection
    st.sidebar.subheader("Univers d'investissement")
    default_tickers = "AAPL,GOOGL,TSLA,MSFT"
    tickers_input = st.sidebar.text_input("Symboles (Yahoo Finance)", default_tickers)
    tickers = [t.strip().upper() for t in tickers_input.split(',')]

    # 2. Allocation
    st.sidebar.subheader("Allocation d'actifs")
    st.sidebar.caption("Définition des pondérations (normalisation automatique à 100%).")
    
    raw_weights = {}
    for t in tickers:
        raw_weights[t] = st.sidebar.slider(f"Poids : {t}", 0.0, 1.0, 1.0/len(tickers))

    # Normalisation des poids
    total_raw = sum(raw_weights.values())
    if total_raw == 0:
        weights = {t: 1/len(tickers) for t in tickers}
    else:
        weights = {k: v/total_raw for k, v in raw_weights.items()}

    # Affichage technique des poids
    st.sidebar.markdown("---")
    st.sidebar.text("Allocation effective :")
    st.sidebar.json({k: f"{v:.2%}" for k, v in weights.items()})

    # --- EXÉCUTION ---
    if st.sidebar.button("Exécuter la simulation", type="primary"):
        try:
            with st.spinner('Récupération des données de marché...'):
                df_prices = get_multiple_data(tickers)
            
            if df_prices.empty:
                st.error("Erreur : Aucune donnée disponible pour les symboles saisis.")
                return

            # Simulation
            portfolio_val = simulate_portfolio(df_prices, weights)
            returns = df_prices.pct_change().dropna()

            # --- AFFICHAGE DES RÉSULTATS ---
            tab1, tab2, tab3 = st.tabs(["Performance Historique", "Corrélation", "Métriques de Risque"])

            with tab1:
                st.subheader("Performance comparée (Base 100)")
                df_normalized = (df_prices / df_prices.iloc[0]) * 100
                df_normalized['Portefeuille Simulé'] = portfolio_val
                
                fig = px.line(df_normalized, title="Trajectoire de valeur : Portefeuille vs Sous-jacents")
                fig.update_layout(xaxis_title="Date", yaxis_title="Valeur (Base 100)")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Matrice de Corrélation des Rendements")
                corr_matrix = returns.corr()
                fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)

            with tab3:
                st.subheader("Analyse de la Volatilité")
                volatility = returns.std()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Volatilité par actif (Écart-type)**")
                    st.bar_chart(volatility)
                with col2:
                    st.markdown("**Statistiques descriptives**")
                    st.dataframe(returns.describe())

        except Exception as e:
            st.error(f"Erreur d'exécution : {e}")

if __name__ == "__main__":
    display_quant_b_dashboard()
