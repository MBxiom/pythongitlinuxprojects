import streamlit as st
import sys
import os

# Page configuration
st.set_page_config(layout="wide", page_title="Financial Engineering Dashboard")

# 1. Import Quant A Module
try:
    from quant_a import run_quant_a
except ImportError:
    st.error("Quant A module not found.")
    def run_quant_a(): pass

# 2. Import Quant B Module
try:
    # Import dashboard from modules/quant_b/dashboard.py
    from modules.quant_b.dashboard import display_quant_b_dashboard
except ImportError:
    # Fallback for different directory structure
    try:
        from quant_b.dashboard import display_quant_b_dashboard
    except:
        st.warning("Quant B module not found. (Check 'modules' folder)")
        def display_quant_b_dashboard(): st.write("Module B is missing.")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Quant A (My Part)", "Quant B (Portfolio)"])

if page == "Home":
    st.title("Financial Engineering Group 12")
    st.markdown("""
    ### Welcome to the Integrated Financial Platform
    This dashboard combines two powerful modules:
    
    * **Quant A:** Single Asset Analysis & AI Prediction
    * **Quant B:** Portfolio Management & Optimization
    
    **Select a module from the sidebar to start.**
    """)
    
elif page == "Quant A (My Part)":
    # Execute Quant A Code
    run_quant_a()

elif page == "Quant B (Portfolio)":
    # Execute Quant B Code
    display_quant_b_dashboard()