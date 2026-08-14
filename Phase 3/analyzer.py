import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

#gathering data to start
def get_stock_data(ticker, period):
    stock_data = yf.Ticker(ticker).history(period=period)
    stock_data['Daily Return'] = stock_data['Close'].pct_change()
    stock_data['Cumulative'] = (1 + stock_data['Daily Return']).cumprod()
    return stock_data

#calculation functions
def total_return(stock_data):
    returns = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]
    return returns * 100

def cumulative(stock_data):
    return (1 + stock_data['Daily Return']).cumprod()

def avg_daily_return(stock_data):
    return stock_data['Daily Return'].mean() * 100

def volatility(stock_data):
    return stock_data['Daily Return'].std() * 100

def sharpe_ratio(stock_data):
    avg = stock_data['Daily Return'].mean()
    vol = stock_data['Daily Return'].std()
    return (avg / vol) * 252 ** 0.5

def max_drawdown(stock_data):
    cumulative = (1 + stock_data['Daily Return']).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min() * 100

#all together
def calculate_metrics(stock_data):
    return {
        'Total Return': total_return(stock_data),
        'Avg Daily Return': avg_daily_return(stock_data),
        'Volatility': volatility(stock_data),
        'Sharpe Ratio': sharpe_ratio(stock_data),
        'Max Drawdown': max_drawdown(stock_data)
    }


#comparison functions
def compare_to_benchmark(stock_data, period):
    benchmark = yf.Ticker('VOO').history(period=period)
    benchmark['Daily Return'] = benchmark['Close'].pct_change()

    benchmark_return = total_return(benchmark)
    benchmark_sharpe = sharpe_ratio(benchmark)

    if benchmark_return > total_return(stock_data):
        greater_return = False 
    else:
        greater_return = True

    if benchmark_sharpe > sharpe_ratio(stock_data):
        greater_sharpe = False
    else:
        greater_sharpe = True

    return {
        'Benchmark Total Return' : benchmark_return,
        'Benchmark Sharpe Ratio' : benchmark_sharpe,
        'Stock Total Return' : total_return(stock_data),
        'Stock Sharpe Ratio' : sharpe_ratio(stock_data),
        'Beats Benchmark Return' : greater_return,
        'Beats Sharpe Ratio' : greater_sharpe
    }

