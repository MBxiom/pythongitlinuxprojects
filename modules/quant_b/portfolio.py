import pandas as pd
import numpy as np

def simulate_portfolio(data, weights):
    
    normalized_data = data / data.iloc[0]

    weight_list = []
    for ticker in data.columns:
        weight_list.append(weights.get(ticker, 0)) 
    
    portfolio_value = normalized_data.dot(weight_list)

    return portfolio_value * 100
