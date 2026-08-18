import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from analyzer import *
from backtester import *
from report import *




#Global Variables
stocks = ['AAPL', 'VTI', 'NVDA', 'JPM', 'JNJ']
line_graphs = ['Cumulative']
bar_graphs = ['Volatility', 'Max Drawdown']
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
def print_results():
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
def create_line_graphs():
    for name in line_graphs:
        for ticker in stocks:
            plt.plot(stock_data[ticker][name].index, stock_data[ticker][name], label=ticker)

        plt.title(name + ' Comparison')
        plt.xlabel('Date')
        plt.ylabel(name)
        plt.legend()
        plt.savefig('outputs/' + name + '_line_graph.png')
        plt.clf()
    

def create_bar_graphs():
    for name in bar_graphs:
        for ticker in stocks:
            plt.bar(ticker, stock_metrics[ticker][name])
        plt.title(name + ' Comparison')
        plt.xlabel('Stock')
        plt.ylabel(name + ' %')
        plt.savefig('outputs/' + name + 'bar_graph.png')
        plt.clf()



#run setup(dont touch)
for ticker in stocks:
    stock_data[ticker] = run_backtester(stock_data[ticker])
backtest_summary = backtester_summary(stock_data, stocks)


#testing
#create_bar_graphs()
#create_line_graphs()
#data = get_stock_data('AAPL', '5y')
#data = generate_signals(data)
#print(data[['Close', '50MA', '200MA', 'Signal']].tail(20))
''' for ticker in stocks:
    stock_data[ticker] = run_backtester(stock_data[ticker])
print(stock_data)
'''
#print(backtester_summary(stock_data, stocks))
generate_report(stock_metrics, comparison, backtest_summary, stocks)

