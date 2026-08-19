import os

import matplotlib
matplotlib.use('Agg')  # write PNGs without opening a window
import matplotlib.pyplot as plt

from analyzer import get_stock_data, calculate_metrics, compare_to_benchmark
from backtester import run_backtester, backtester_summary
from database import (init_db, save_prices, load_prices, has_fresh_data,
                      save_metrics, save_backtest_result,
                      strategy_leaderboard, strategy_averages)
from ml_strategy import ml_summary
from report import generate_report

STOCKS = ['AAPL', 'VTI', 'NVDA', 'JPM', 'JNJ']
PERIOD = '5y'
OUTPUT_DIR = 'outputs'

LINE_GRAPHS = ['Cumulative']
BAR_GRAPHS = ['Volatility', 'Max Drawdown']

RUN_ML = True  # walk-forward retrains ~56 model pairs per stock; slow but honest


# checks SQLite first and only calls yfinance when the cache is missing or stale
def fetch_prices(ticker, period=PERIOD):
    if has_fresh_data(ticker):
        print(f'  {ticker}: loaded from database')
        return load_prices(ticker)

    print(f'  {ticker}: fetching from yfinance')
    data = get_stock_data(ticker, period)
    save_prices(ticker, data)
    return data


def print_results(stock_metrics, comparison, backtest_summary):
    for ticker in STOCKS:
        m = stock_metrics[ticker]
        c = comparison[ticker]
        b = backtest_summary[ticker]

        print(f'''
---------- {ticker} ----------
Total Return:        {m['Total Return']:.2f}%
Avg Daily Return:    {m['Avg Daily Return']:.2f}%
Volatility:          {m['Volatility']:.2f}%
Sharpe Ratio:        {m['Sharpe Ratio']:.2f}
Max Drawdown:        {m['Max Drawdown']:.2f}%
Beats Benchmark Return: {c['Beats Benchmark Return']}
Beats Benchmark Sharpe: {c['Beats Sharpe Ratio']}
MA Crossover:        {b['Strategy Return']:.2f}x  (in market {b['Exposure']:.1%})
Buy and Hold:        {b['No Strategy Return']:.2f}x''')


def create_line_graphs(stock_data):
    for name in LINE_GRAPHS:
        for ticker in STOCKS:
            series = stock_data[ticker][name]
            plt.plot(series.index, series, label=ticker)

        plt.title(f'{name} Returns Comparison')
        plt.xlabel('Date')
        plt.ylabel(name)
        plt.legend()
        plt.savefig(os.path.join(OUTPUT_DIR, f'{name}_line_graph.png'))
        plt.clf()


def create_bar_graphs(stock_metrics):
    for name in BAR_GRAPHS:
        for ticker in STOCKS:
            plt.bar(ticker, stock_metrics[ticker][name])

        plt.title(f'{name} Comparison')
        plt.xlabel('Stock')
        plt.ylabel(f'{name} %')
        plt.savefig(os.path.join(OUTPUT_DIR, f'{name}_bar_graph.png'))
        plt.clf()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    init_db()

    stock_data = {}
    stock_metrics = {}
    comparison = {}

    print('Loading price data...')
    for ticker in STOCKS:
        stock_data[ticker] = fetch_prices(ticker)
        stock_metrics[ticker] = calculate_metrics(stock_data[ticker])
        comparison[ticker] = compare_to_benchmark(stock_data[ticker], PERIOD)

        save_metrics(ticker, stock_metrics[ticker])

    print('\nRunning MA crossover backtest...')
    for ticker in STOCKS:
        stock_data[ticker] = run_backtester(stock_data[ticker])

    backtest_summary = backtester_summary(stock_data, STOCKS)

    for ticker in STOCKS:
        b = backtest_summary[ticker]
        save_backtest_result(ticker, 'ma_crossover',
                             b['Strategy Return'], b['Exposure'])
        save_backtest_result(ticker, 'buy_and_hold',
                             b['No Strategy Return'], 1.0)

    if RUN_ML:
        print('\nRunning walk-forward ML backtest (this takes a few minutes)...')
        for ticker in STOCKS:
            print(f'  {ticker}...')
            results = ml_summary(stock_data[ticker])

            if results is None:
                print(f'  {ticker}: not enough history, skipped')
                continue

            save_backtest_result(ticker, 'logistic_regression',
                                 results['lr_return'], results['lr_exposure'])
            save_backtest_result(ticker, 'random_forest',
                                 results['rf_return'], results['rf_exposure'])

    print_results(stock_metrics, comparison, backtest_summary)

    print('\nGenerating charts...')
    create_line_graphs(stock_data)
    create_bar_graphs(stock_metrics)

    print('Generating PDF report...')
    generate_report(stock_metrics, comparison, backtest_summary, STOCKS)

    # everything below is read back out of SQLite, not from the dicts above
    print('\n===== Strategy leaderboard (AAPL) =====')
    for name, ret, exposure in strategy_leaderboard('AAPL'):
        print(f'{name:22s} {ret:6.2f}x   in market {exposure:.1%}')

    print('\n===== Average across all tickers =====')
    for name, avg_ret, avg_exp, n in strategy_averages():
        print(f'{name:22s} {avg_ret:6.2f}x   in market {avg_exp:.1%}   n={n}')

    print('\nDone.')


if __name__ == '__main__':
    main()