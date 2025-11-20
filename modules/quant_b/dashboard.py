import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DU CHEMIN ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)
# -----------------------------

from modules.quant_b.data_retrieval import get_multiple_data
from modules.quant_b.portfolio import simulate_portfolio

def display_quant_b_dashboard():
    st.set_page_config(page_title="Analyse Portfolio", layout="wide")
    st.title("Analyse Multivariée & Simulation de Portefeuille")

    # --- SIDEBAR ---
    st.sidebar.header("Paramètres de Simulation")
    
    # 1. Univers
    st.sidebar.subheader("1. Sélection d'actifs")
    default_tickers = "AAPL,GOOGL,TSLA,MSFT"
    tickers_input = st.sidebar.text_input("Symboles (Ticker)", default_tickers)
    tickers = [t.strip().upper() for t in tickers_input.split(',')]

    # 2. Allocation
    st.sidebar.subheader("2. Pondération")
    st.sidebar.caption("Ajustement des poids (Normalisation auto).")
    
    raw_weights = {}
    for t in tickers:
        raw_weights[t] = st.sidebar.slider(f"{t}", 0.0, 1.0, 1.0/len(tickers))

    # Normalisation
    total_raw = sum(raw_weights.values())
    if total_raw == 0:
        weights = {t: 1/len(tickers) for t in tickers}
    else:
        weights = {k: v/total_raw for k, v in raw_weights.items()}

    # --- MODIFICATION ICI : Tableau PROPRE au lieu de JSON ---
    st.sidebar.markdown("---")
    st.sidebar.write("**Allocation cible :**")
    
    # Création d'un DataFrame pour un affichage propre sans accolades {}
    df_weights = pd.DataFrame.from_dict(weights, orient='index', columns=['Poids'])
    df_weights['Poids'] = df_weights['Poids'].apply(lambda x: f"{x:.1%}") 
    st.sidebar.table(df_weights)
    # ---------------------------------------------------------

    # --- BOUTON ---
    if st.sidebar.button("Lancer l'Analyse", type="primary"):
        try:
            with st.spinner('Calcul des indicateurs en cours...'):
                df_prices = get_multiple_data(tickers)
            
            if df_prices.empty:
                st.error("Erreur : Données de marché indisponibles.")
                return

            # Simulation
            portfolio_val = simulate_portfolio(df_prices, weights)
            returns = df_prices.pct_change().dropna()

            # --- ONGLETS ---
            tab1, tab2, tab3 = st.tabs(["Performance", "Corrélation", "Risque & Volatilité"])

            with tab1:
                st.subheader("Performance Historique (Base 100)")
                df_normalized = (df_prices / df_prices.iloc[0]) * 100
                df_normalized['Portefeuille'] = portfolio_val
                
                fig = px.line(df_normalized)
                fig.update_layout(xaxis_title="Date", yaxis_title="Valeur Indexée", showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Matrice de Corrélation")
                corr_matrix = returns.corr()
                fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)

            with tab3:
                st.subheader("Analyse du Risque")
                volatility = returns.std()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Volatilité (Écart-type)**")
                    st.bar_chart(volatility)
                with col2:
                    st.markdown("**Statistiques Détaillées**")
                    st.dataframe(returns.describe())

        except Exception as e:
            st.error(f"Erreur système : {e}")

if __name__ == "__main__":
    display_quant_b_dashboard()
