import streamlit as st
import sys
import os
import pandas as pd
import numpy as np  
import plotly.express as px

# chemin d'accès
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)


from modules.quant_b.data_retrieval import get_multiple_data
from modules.quant_b.portfolio import simulate_portfolio

def display_quant_b_dashboard():
    st.set_page_config(page_title="Analyse du Portfolio", layout="wide")
    st.title("Analyse Multivariée et simulation de Portefeuille")

    # sidebar
    st.sidebar.header("Paramètres de Simulation")
    
    # créer l'univers
    st.sidebar.subheader("Sélectionner les actifs")
    default_tickers = "AAPL,GOOGL,TSLA,MSFT"
    tickers_input = st.sidebar.text_input("Symboles (Ticker)", default_tickers)
    tickers = [t.strip().upper() for t in tickers_input.split(',')]

    # allocation
    st.sidebar.subheader("Pondération")
    st.sidebar.caption("Ajustement des poids (Normalisation automatique).")
    
    raw_weights = {}
    for t in tickers:
        raw_weights[t] = st.sidebar.slider(f"{t}", 0.0, 1.0, 1.0/len(tickers))

    # normalisation
    total_raw = sum(raw_weights.values())
    if total_raw == 0:
        weights = {t: 1/len(tickers) for t in tickers}
    else:
        weights = {k: v/total_raw for k, v in raw_weights.items()}

    # fréquence de réequilibrage 
    st.sidebar.subheader("Stratégie")
    rebalance_freq = st.sidebar.selectbox(
        "Fréquence de rééquilibrage",
        ["Jamais (buy and hold)", "Mensuel", "Trimestriel", "Annuel"],
        index=0
    )
    

    st.sidebar.markdown("---")
    st.sidebar.write("**Allocation cible :**")
    
    df_weights = pd.DataFrame.from_dict(weights, orient='index', columns=['Poids'])
    df_weights['Poids'] = df_weights['Poids'].apply(lambda x: f"{x:.1%}") 
    st.sidebar.table(df_weights)

    # bouton lancer l'analyse
    if st.sidebar.button("Lancer l'analyse", type="primary"):
        try:
            with st.spinner('Calcul des indicateurs en cours...'):
                df_prices = get_multiple_data(tickers)
            
            if df_prices.empty:
                st.error("Les données de marché sont malheureusement indisponible.")
                return

            # calculs
            #valeur du protfolio serie temporelle
            portfolio_val = simulate_portfolio(df_prices, weights)
            
            #rendements individuels des actifs
            returns = df_prices.pct_change().dropna()

            # KPI du portefeuille gloobal
            # ses rendements journaliers
            portfolio_returns = portfolio_val.pct_change().dropna()
            
            # métriques anuelles (252 jours)
            total_return = (portfolio_val.iloc[-1] / portfolio_val.iloc[0]) - 1
            annual_volatility = portfolio_returns.std() * np.sqrt(252)
            annual_mean_return = portfolio_returns.mean() * 252
            sharpe_ratio = annual_mean_return / annual_volatility if annual_volatility != 0 else 0

            # affichage synthèse
            st.markdown("Synthèse du portefeuille")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Rendement total", f"{total_return:+.2%}", help="Performance cumulée sur la période")
            kpi2.metric("Volatilité année", f"{annual_volatility:.2%}", help="Risque annualisé")
            kpi3.metric("Ratio de Sharpe", f"{sharpe_ratio:.2f}", help="Rendement ajusté du risque")
            st.markdown("---")
            

            # onglets de navigation
            tab1, tab2, tab3 = st.tabs(["Performance", "Corrélation", "Risque et diversification"])

            with tab1:
                st.subheader("Performance historique (Base 100)")
                # normalisation pour comparer visuellement
                df_normalized = (df_prices / df_prices.iloc[0]) * 100
                df_normalized['Portefeuille'] = portfolio_val
                
                fig = px.line(df_normalized)
                fig.update_layout(xaxis_title="Date", yaxis_title="Valeur Indexée (Base 100)", showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Matrice de corrélation des rendements")
                corr_matrix = returns.corr()
                fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)

            with tab3:
                st.subheader("Analyse du Risque")
                
                # volatilité individuelle vs porterfeuille 
                volatility_indiv = returns.std() * np.sqrt(252)
                
                # Analyse de diversification
                st.info(" **Effet de diversification")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Volatilité par actif vs Portefeuille**")
                    # On crée un DF pour comparer
                    df_vol = pd.DataFrame(volatility_indiv, columns=["Volatilité"])
                    # On ajoute le portefeuille pour comparer
                    df_vol.loc["PORTEFEUILLE"] = annual_volatility
                    
                    # Graphique en barres colorés pour distinguer le portefeuille
                    st.bar_chart(df_vol)
                
                with col2:
                    st.markdown("**Statistiques Détaillées (Rendements journaliers)**")
                    st.dataframe(returns.describe())
                

        except Exception as e:
            st.error(f"Erreur système : {e}")

if __name__ == "__main__":
    display_quant_b_dashboard()
