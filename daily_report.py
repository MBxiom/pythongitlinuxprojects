import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os

# 설정
TICKER = "EURKRW=X"
REPORT_FILE = "daily_report.txt"

def calculate_metrics(ticker):
    # 오늘 데이터 가져오기
    data = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=False)

    # MultiIndex 처리 (데이터 껍질 벗기기)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 최신 데이터
    today_data = data.iloc[-1]
    close_price = float(today_data['Close'])
    open_price = float(today_data['Open'])

    # 수익률 및 변동성 계산
    data['Return'] = data['Close'].pct_change()
    volatility = data['Return'].std() * np.sqrt(252) # 연환산 변동성

    # MDD (최대 낙폭) 계산
    cum_ret = (1 + data['Return']).cumprod()
    peak = cum_ret.cummax()
    mdd = ((cum_ret - peak) / peak).min()

    return open_price, close_price, volatility, mdd

def save_report():
    try:
        open_p, close_p, vol, mdd = calculate_metrics(TICKER)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_content = f"""
[Daily Report - {now}]
Asset: {TICKER}
Open: {open_p:.2f}
Close: {close_p:.2f}
Volatility (Ann.): {vol:.2%}
Max Drawdown: {mdd:.2%}
-----------------------------------
"""
        # 파일에 추가 (Append mode)
        # 리눅스 서버의 절대 경로를 사용하여 저장
        file_path = os.path.join(os.getcwd(), REPORT_FILE)
        with open(file_path, "a") as f:
            f.write(report_content)

        print(f"Report generated successfully at {now}")

    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    save_report()
