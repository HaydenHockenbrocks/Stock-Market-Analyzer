import os

import matplotlib
matplotlib.use('Agg')  # write PNGs without opening a window
import matplotlib.pyplot as plt

from analyzer import get_stock_data, calculate_metrics, compare_to_benchmark
from backtester import run_backtester, backtester_summary
from database import (init_db, save_prices, load_prices, has_fresh_data,
                      save_metrics, save_backtest_result,
                      strategy_leaderboard, strategy_averages,
                      window_consistency_check)
from ml_strategy import ml_summary
from report import generate_report

STOCKS = ['AAPL', 'VTI', 'NVDA', 'JPM', 'JNJ']
BENCHMARK = 'VOO'
PERIOD = '5y'
OUTPUT_DIR = 'outputs'

LINE_GRAPHS = ['Cumulative']
BAR_GRAPHS = ['Volatility', 'Max Drawdown']

# walk-forward retrains ~56 model pairs per stock, so this is the slow part.
# Set False to test the rest of the pipeline quickly.
RUN_ML = True


# checks SQLite first and only calls yfinance when the cache is missing or stale
def fetch_prices(ticker, period=PERIOD):
    if has_fresh_data(ticker):
        print(f'  {ticker}: loaded from database')
        return load_prices(ticker)

    print(f'  {ticker}: fetching from yfinance')
    data = get_stock_data(ticker, period)
    save_prices(ticker, data)
    return data


def print_results(stock_metrics, comparison, backtest_summary, ml_results):
    for ticker in STOCKS:
        m = stock_metrics[ticker]
        c = comparison[ticker]
        b = backtest_summary[ticker]

        print(f'''
---------- {ticker} ----------
Total Return (5y):     {m['Total Return']:.2f}%
Avg Daily Return:      {m['Avg Daily Return']:.2f}%
Daily Volatility:      {m['Volatility']:.2f}%
Sharpe Ratio (ann.):   {m['Sharpe Ratio']:.2f}
Max Drawdown:          {m['Max Drawdown']:.2f}%
Beats {BENCHMARK} on return: {c['Beats Benchmark Return']}
Beats {BENCHMARK} on Sharpe: {c['Beats Sharpe Ratio']}

Backtest window: {b['n_days']} days from {b['start_date'].date()}
  Buy and hold:      {b['No Strategy Return']:.2f}x
  MA crossover:      {b['Strategy Return']:.2f}x  (in market {b['Exposure']:.1%})''')

        if ml_results.get(ticker):
            r = ml_results[ticker]
            print(f"  Random forest:     {r['rf_return']:.2f}x  "
                  f"(in market {r['rf_exposure']:.1%})")
            print(f"  Logistic regr.:    {r['lr_return']:.2f}x  "
                  f"(in market {r['lr_exposure']:.1%})")
            print(f"  Actual up days:    {r['base_rate']:.1%}")


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
    labels = {'Volatility': 'Daily Volatility %', 'Max Drawdown': 'Max Drawdown %'}

    for name in BAR_GRAPHS:
        for ticker in STOCKS:
            plt.bar(ticker, stock_metrics[ticker][name])

        plt.title(f'{name} Comparison')
        plt.xlabel('Stock')
        plt.ylabel(labels.get(name, name))
        plt.savefig(os.path.join(OUTPUT_DIR, f'{name}_bar_graph.png'))
        plt.clf()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    init_db()

    stock_data = {}
    stock_metrics = {}
    comparison = {}

    # benchmark comes from the same cache as everything else, fetched once
    print('Loading price data...')
    benchmark_data = fetch_prices(BENCHMARK)

    for ticker in STOCKS:
        stock_data[ticker] = fetch_prices(ticker)
        stock_metrics[ticker] = calculate_metrics(stock_data[ticker])
        comparison[ticker] = compare_to_benchmark(stock_data[ticker], benchmark_data)
        save_metrics(ticker, stock_metrics[ticker])

    for ticker in STOCKS:
        stock_data[ticker] = run_backtester(stock_data[ticker])

    # ML runs first because it defines the shortest window. Every other strategy
    # is then trimmed to match, so all cumulative returns cover the same period.
    ml_results = {}
    ml_start_dates = {}

    if RUN_ML:
        print('\nRunning walk-forward ML backtest (this takes a few minutes)...')
        for ticker in STOCKS:
            print(f'  {ticker}...')
            results = ml_summary(stock_data[ticker])

            if results is None:
                print(f'    not enough history, skipped')
                continue

            ml_results[ticker] = results
            ml_start_dates[ticker] = results['start_date']

    backtest_summary = backtester_summary(stock_data, STOCKS, ml_start_dates)

    for ticker in STOCKS:
        b = backtest_summary[ticker]
        n_days = b['n_days']
        start = b['start_date']

        save_backtest_result(ticker, 'buy_and_hold', b['No Strategy Return'],
                             1.0, n_days, start)
        save_backtest_result(ticker, 'ma_crossover', b['Strategy Return'],
                             b['Exposure'], n_days, start)

        if ml_results.get(ticker):
            r = ml_results[ticker]
            save_backtest_result(ticker, 'logistic_regression', r['lr_return'],
                                 r['lr_exposure'], r['n_days'], r['start_date'])
            save_backtest_result(ticker, 'random_forest', r['rf_return'],
                                 r['rf_exposure'], r['n_days'], r['start_date'])

    print_results(stock_metrics, comparison, backtest_summary, ml_results)

    print('\nGenerating charts...')
    create_line_graphs(stock_data)
    create_bar_graphs(stock_metrics)

    print('Generating PDF report...')
    generate_report(stock_metrics, comparison, backtest_summary, STOCKS,
                    ml_results, os.path.join(OUTPUT_DIR, 'report.pdf'))

    # read back out of SQLite rather than from the dicts above
    print('\n===== Strategy leaderboard: AAPL =====')
    for name, ret, exposure, n_days, start in strategy_leaderboard('AAPL'):
        print(f'{name:22s} {ret:6.2f}x   in market {exposure:6.1%}   '
              f'{n_days} days from {start}')

    aligned = window_consistency_check('AAPL')
    print(f'All strategies share one window: {aligned}')

    print('\n===== Averaged across all tickers =====')
    for name, avg_ret, avg_exp, n in strategy_averages():
        print(f'{name:22s} {avg_ret:6.2f}x   in market {avg_exp:6.1%}   n={n}')

    print('\nDone.')


if __name__ == '__main__':
    main()