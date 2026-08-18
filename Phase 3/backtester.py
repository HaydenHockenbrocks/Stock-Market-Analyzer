import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from analyzer import *



#defining support functions
def moving_average_fifty(stock_data):
    return stock_data['Close'].rolling(window=50).mean()

def moving_average_twohundred(stock_data):
    return stock_data['Close'].rolling(window=200).mean()


def generate_signals(stock_data):
    stock_data['200MA'] = moving_average_twohundred(stock_data)
    stock_data['50MA'] = moving_average_fifty(stock_data)
    stock_data['Signal'] = (stock_data['50MA'] > stock_data['200MA']).astype(int)
    return stock_data

def strategy_return(stock_data):
    stock_data['Strategy Return'] = stock_data['Daily Return'] * stock_data['Signal'].shift(1)
    return stock_data

def cumulative_return(stock_data):
    stock_data['Cumulative Return'] = (1 + stock_data['Strategy Return']).cumprod()


#main function
def run_backtester(stock_data):
    generate_signals(stock_data)
    strategy_return(stock_data)
    cumulative_return (stock_data)
    return stock_data

#clean_summary
def backtester_summary(stock_data, stocks):
    final_data = {}
    for stock in stocks:
        final_data[stock] = {}
        final_data[stock]['Strategy Return'] = stock_data[stock]['Cumulative Return'].iloc[-1]
        final_data[stock]['No Strategy Return'] = stock_data[stock]['Cumulative'].iloc[-1]
        final_data[stock]['Good Strategy'] = final_data[stock]['Strategy Return'] > final_data[stock]['No Strategy Return']
    return final_data

    

    






