# Financial Engineering Dashboard 

## Project Overview
This project is an integrated financial platform designed to support portfolio managers with quantitative tools. [cite_start]It simulates a professional workflow using Git, Linux, and Python[cite: 13]. The dashboard consists of two main modules:
* [cite_start]**Quant A (Single Asset):** Univariate analysis, backtesting strategies, and AI-based price prediction[cite: 31, 36].
* [cite_start]**Quant B (Portfolio):** Multivariate analysis, portfolio optimization, and risk management metrics[cite: 38].

[cite_start]The application retrieves real-time financial data and provides an interactive dashboard for professional use[cite: 6].

## Team Members
* **Member 1 (Quant A):** [Seunghyeon Kim]
* **Member 2 (Quant B):** [Martin Bouleuc]

---

## Key Features

### 1. Quant A: Single Asset Analysis
* **Real-time Data:** Fetches live data for asset EUR/KRW
* [cite_start]**Backtesting Strategies:** Compare 'Buy-and-Hold' strategy vs. 'SMA Crossover' strategy with adjustable parameters[cite: 33].
* [cite_start]**Performance Metrics:** Sharpe Ratio, Max Drawdown (MDD), Cumulative Returns[cite: 34].
* [cite_start]**AI Prediction (Bonus Feature):** Future price forecasting using Machine Learning (Linear Regression) with 95% confidence intervals[cite: 36, 62].

### 2. Quant B: Portfolio Management
* [cite_start]**Multi-Asset Simulation:** Construct portfolios with AAPL, GOOGL, MSFT, TSLA, etc.[cite: 41].
* **Optimization Tools:** Adjust asset weights dynamically to simulate portfolio scenarios.
* [cite_start]**Risk Metrics:** Portfolio Volatility, Expected Return, Diversification Effect, and Sharpe Ratio[cite: 42].
* [cite_start]**Visualization:** Correlation Matrix Heatmap and Wealth Curve comparison (Portfolio vs Assets)[cite: 42, 44].

### 3. System Automation
* [cite_start]**24/7 Availability:** Deployed on AWS Linux Server using background processes[cite: 25].
* [cite_start]**Daily Reporting:** Automated daily reports generated via `cron` (executed daily at 20:00)[cite: 22].
* [cite_start]**Modular Structure:** Clean separation of concerns (`modules/`, `scripts/`, `data/`)[cite: 57].

---

## Installation & Usage

### Prerequisites
* Python 3.9+
* Streamlit
* Plotly, yfinance, scikit-learn

### 1. Clone the Repository
```bash
git clone [https://github.com/MBxiom/pythongitlinuxprojects.git](https://github.com/MBxiom/pythongitlinuxprojects.git)
cd pythongitlinuxprojects

```bash
# 1. Download code
git clone [https://github.com/MBxiom/pythongitlinuxprojects.git](https://github.com/MBxiom/pythongitlinuxprojects.git)
cd pythongitlinuxprojects

# 2. Install libraries
pip install -r requirements.txt

# 3. Run dashboard
streamlit run main.py

Automation (Cron Job)
Used Linux crontab to run the report automatically every day at 8 PM.
0 20 * * * /usr/bin/python3 /home/ec2-user/pythongitlinuxprojects/daily_report.py >> /home/ec2-user/pythongitlinuxprojects/cron.log 2>&1
