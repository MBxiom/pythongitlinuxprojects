# pythongitlinuxprojects
# Financial Dashboard Project (Quant A)

This project is a comprehensive financial dashboard built with **Python**, **Streamlit**, and **Linux**. It provides real-time single asset analysis, quantitative strategy backtesting, and AI-based price prediction.

## Live Demo
Access the live dashboard here: [http://13.38.4.57:8501](http://13.38.4.57:8501)

## Features (Quant A Module)
- **Real-time Data:** Retrieves financial data using `yfinance` API.
- **Strategy Backtesting:**
  - Simple Moving Average (SMA) Crossover
  - Momentum Strategy
- **AI Prediction:** Predicts next-day closing price using Linear Regression (Machine Learning).
- **Automated Reporting:** Generates daily reports via Linux Cron job every day at 8 PM.

## Tech Stack
- **Language:** Python 3.9
- **Framework:** Streamlit
- **Libraries:** Pandas, NumPy, Plotly, Scikit-learn, Yfinance
- **Infrastructure:** AWS EC2 (Amazon Linux), Git/GitHub

## Project Structure
```text
├── quant_a.py        # Main application (Quant A module)
├── daily_report.py   # Script for daily automated reporting (Cron)
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation

