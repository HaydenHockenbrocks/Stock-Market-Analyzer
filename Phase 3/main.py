import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from analyzer import *

#Global Variables
stocks = ['AAPL', 'VTI', 'NVDA', 'JPM', 'JNJ']
period = '5y'
stock_data = {}
stock_metrics= {}
comparison = {}

#Gathering Data
for ticker in stocks:
    stock_data[ticker] = get_stock_data(ticker, period)
    stock_metrics[ticker] = calculate_metrics(stock_data[ticker])
    comparison[ticker] = compare_to_benchmark(stock_data[ticker], period)

#print results
for ticker in stocks:
    print(f'''
----------{ticker}----------
Total Return: {stock_metrics[ticker]['Total Return']:.2f}
Avg Daily Return: {stock_metrics[ticker]['Avg Daily Return']:.2f}
Volatility: {stock_metrics[ticker]['Volatility']:.2f}
Sharpe Ratio: {stock_metrics[ticker]['Sharpe Ratio']:.2f}
Max Drawdown: {stock_metrics[ticker]['Max Drawdown']:.2f}
Greater Benchmark Return: {comparison[ticker]['Beats Benchmark Return']}
Greater Sharpe Ratio Than Benchmark: {comparison[ticker]['Beats Sharpe Ratio']}
''')

#creating and putputing graphs
for ticker in stocks:
    plt.plot(stock_data[ticker]['Cumulative'].index, stock_data[ticker]['Cumulative'], label=ticker)

plt.title('Cumulative Returns Comparison')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.savefig('outputs/cumulative_returns.png')

