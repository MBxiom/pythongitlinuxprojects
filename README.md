# Financial Dashboard (Quant A)

This project is a dashboard for financial data analysis and stock price prediction.
It is deployed on AWS EC2.

## 1. Live Link
* **URL:** http://13.38.4.57:8501

## 2. My Features (Quant A)
* **Stock Analysis:** Moving Average & Momentum Strategy.
* **AI Prediction (Bonus):** Predicted next day's price using Linear Regression.

## 3. How to Run (Commands)
If you want to run this locally:

```bash
# 1. Download code
git clone [https://github.com/MBxiom/pythongitlinuxprojects.git](https://github.com/MBxiom/pythongitlinuxprojects.git)
cd pythongitlinuxprojects

# 2. Install libraries
pip install streamlit yfinance pandas scikit-learn plotly

# 3. Run dashboard
streamlit run main.py

Automation (Cron Job)
Used Linux crontab to run the report automatically every day at 8 PM.
0 20 * * * /usr/bin/python3 /home/ec2-user/pythongitlinuxprojects/daily_report.py >> /home/ec2-user/pythongitlinuxprojects/cron.log 2>&1
