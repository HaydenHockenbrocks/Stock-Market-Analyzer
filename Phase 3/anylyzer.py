import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def get_stock_data(ticker, period):
    stock_data = yf.Ticker(ticker).history(period=period)
    stock_data['Daily Return'] = stock_data['Close'].pct_change()
    return stock_data

print(get_stock_data('AAPL', '5y'))

    