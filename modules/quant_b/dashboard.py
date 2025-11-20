import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px

# --- PATH FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)
# ----------------

from modules.quant_b.data_retrieval import get_multiple_data
from modules.quant_b.portfolio import simulate_portfolio

def display_quant_b_dashboard():
    st.set_page_config(page_title="Dashboard Quant B", layout="wide")
    st.title("💰 Gestion de Portefeuille (Quant B)")

    # --- SIDEBAR ---
    st.sidebar.header("Paramètres")
    default_tickers = "AAPL,GOOGL,TSLA,MSFT"
    tickers_input = st.sidebar.text_input("Actifs (via Yahoo Finance)", default_tickers)
    tickers = [t.strip().upper() for t in tickers_input.split(',')]

    # --- MAIN LOGIC ---
    if st.sidebar.button("🔄 Lancer l'analyse", type="primary"):
        try:
            with st.spinner(f'Récupération des données pour {tickers}...'):
                df_prices = get_multiple_data(tickers)
            
            if df_prices.empty:
                st.error("Aucune donnée récupérée. Vérifiez les symboles.")
                return

            st.success("Données chargées avec succès !")

            # Calculs préliminaires (Rendements)
            returns = df_prices.pct_change().dropna()
            
            # Poids (Equipondéré)
            weights = {t: 1/len(tickers) for t in tickers}
            
            # Simulation Portefeuille
            portfolio_val = simulate_portfolio(df_prices, weights)
            
            # --- AFFICHAGE EN ONGLETS ---
            tab1, tab2, tab3 = st.tabs(["📈 Performance", "🔥 Corrélation", "📊 Risque & Métriques"])

            with tab1:
                st.subheader("Comparaison Normalisée (Base 100)")
                df_normalized = (df_prices / df_prices.iloc[0]) * 100
                df_normalized['Portfolio'] = portfolio_val
                
                fig = px.line(df_normalized, title="Evolution du Portefeuille vs Actifs")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Matrice de Corrélation des Rendements")
                st.markdown("Une valeur proche de **1** signifie que les actifs bougent ensemble.")
                
                corr_matrix = returns.corr()
                fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)

            with tab3:
                st.subheader("Analyse de Volatilité (Risque)")
                
                # Calcul volatilité (Standard Deviation)
                volatility = returns.std()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Volatilité par Actif :**")
                    st.bar_chart(volatility)
                
                with col2:
                    st.write("**Statistiques descriptives :**")
                    st.dataframe(returns.describe())

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    display_quant_b_dashboard()
