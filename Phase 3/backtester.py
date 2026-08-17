import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from analyzer import *

def moving_average_fifty(stock_data):
    return stock_data['Close'].rolling(window=50).mean()

def moving_average_twohundred(stock_data):
    return stock_data['Close'].rolling(window=200).mean()



def generate_signals(stock_data):
    stock_data['200MA'] = moving_average_twohundred(stock_data)
    stock_data['50MA'] = moving_average_fifty(stock_data)
    stock_data['Signal'] = (stock_data['50MA'] > stock_data['200MA']).astype(int)
    return stock_data
        






