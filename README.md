# Financial Engineering Dashboard

## Project Overview
This project is an integrated financial platform designed to support portfolio managers with quantitative tools. It simulates a professional workflow using Git, Linux, and Python. The dashboard consists of two main modules:
* **Quant A (Single Asset):** Univariate analysis, backtesting strategies, and AI-based price prediction.
* **Quant B (Portfolio):** Multivariate analysis, portfolio optimization, and risk management metrics.

The application retrieves real-time financial data and provides an interactive dashboard for professional use.

## Team Members
* **Member 1 (Quant A):** Seunghyeon Kim
* **Member 2 (Quant B):** Martin Bouleuc

---

## Key Features

### 1. Quant A: Single Asset Analysis
* **Real-time Data:** Fetches live data for asset EUR/KRW.
* **Backtesting Strategies:** Compare 'Buy-and-Hold' strategy vs. 'SMA Crossover' strategy with adjustable parameters.
* **Performance Metrics:** Sharpe Ratio, Max Drawdown (MDD), Cumulative Returns.
* **AI Prediction (Bonus Feature):** Future price forecasting using Machine Learning (Linear Regression) with 95% confidence intervals.

### 2. Quant B: Portfolio Management
* **Multi-Asset Simulation:** Construct portfolios with AAPL, GOOGL, MSFT, TSLA, etc.
* **Optimization Tools:** Adjust asset weights dynamically to simulate portfolio scenarios.
* **Risk Metrics:** Portfolio Volatility, Expected Return, Diversification Effect, and Sharpe Ratio.
* **Visualization:** Correlation Matrix Heatmap and Wealth Curve comparison (Portfolio vs Assets).

### 3. System Automation
* **24/7 Availability:** Deployed on AWS Linux Server using background processes.
* **Daily Reporting:** Automated daily reports generated via `cron` (executed daily at 20:00).
* **Modular Structure:** Clean separation of concerns (`modules/`, `scripts/`, `data/`).

---

## Installation & Usage

If you want to run this locally, follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/MBxiom/pythongitlinuxprojects.git](https://github.com/MBxiom/pythongitlinuxprojects.git)
cd pythongitlinuxprojects

2. Install Dependencies
Bash

pip install -r requirements.txt
3. Run the Dashboard
Bash

streamlit run main.py
Access the dashboard at: http://localhost:8501

🕒 Automation (Cron Job)
We used Linux crontab to run the report automatically every day at 8 PM.

Bash

0 20 * * * /usr/bin/python3 /home/ec2-user/pythongitlinuxprojects/daily_report.py >> /home/ec2-user/pythongitlinuxprojects/cron.log 2>&1

Project Structure

- main.py: Entry point of the Streamlit application.

- modules/: Contains quant_a and quant_b logic packages.

- daily_report.py: Script for generating automated daily reports.

- requirements.txt: List of dependencies.
