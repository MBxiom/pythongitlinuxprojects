import streamlit as st
import sys
import os

# Page configuration
st.set_page_config(layout="wide", page_title="Financial Engineering Dashboard")

# 1. Import Quant A Module (FROM MODULES FOLDER)
try:
    # [Changed] Now pointing to modules/quant_a/dashboard.py
    from modules.quant_a.dashboard import run_quant_a
except ImportError:
    st.error("Quant A module not found in 'modules/quant_a/dashboard.py'.")
    def run_quant_a(): pass

# 2. Import Quant B Module
try:
    from modules.quant_b.dashboard import display_quant_b_dashboard
except ImportError:
    st.warning("Quant B module not found.")
    def display_quant_b_dashboard(): st.write("Module B is missing.")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Quant A", "Quant B"])

if page == "Home":
    st.title("Financial Engineering Dashboard")
    st.markdown("""
    ### Welcome to the Integrated Financial Platform
    This dashboard combines two powerful modules:
    
    * **Quant A:** Single Asset Analysis & AI Prediction
    * **Quant B:** Portfolio Management & Optimization
    
    **Select a module from the sidebar to start.**
    """)
    
elif page == "Quant A":
    # Execute Quant A Code
    run_quant_a()

elif page == "Quant B":
    # Execute Quant B Code
    display_quant_b_dashboard()
