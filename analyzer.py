import yfinance as yf


# pulls raw price history and attaches the two derived columns
# every other module expects to find
def get_stock_data(ticker, period):
    stock_data = yf.Ticker(ticker).history(period=period)
    stock_data['Daily Return'] = stock_data['Close'].pct_change()
    stock_data['Cumulative'] = (1 + stock_data['Daily Return']).cumprod()
    return stock_data


# ----- individual metrics -----

def total_return(stock_data):
    first = stock_data['Close'].iloc[0]
    last = stock_data['Close'].iloc[-1]
    return ((last - first) / first) * 100


def avg_daily_return(stock_data):
    return stock_data['Daily Return'].mean() * 100


# daily standard deviation, NOT annualized (see sharpe_ratio, which is)
def volatility(stock_data):
    return stock_data['Daily Return'].std() * 100


# annualized: daily return / daily vol, scaled by sqrt(252 trading days)
def sharpe_ratio(stock_data):
    avg = stock_data['Daily Return'].mean()
    vol = stock_data['Daily Return'].std()
    return (avg / vol) * 252 ** 0.5


# worst peak-to-trough decline over the period
def max_drawdown(stock_data):
    cumulative = (1 + stock_data['Daily Return']).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min() * 100


def calculate_metrics(stock_data):
    return {
        'Total Return': total_return(stock_data),
        'Avg Daily Return': avg_daily_return(stock_data),
        'Volatility': volatility(stock_data),
        'Sharpe Ratio': sharpe_ratio(stock_data),
        'Max Drawdown': max_drawdown(stock_data)
    }


# benchmark_data is passed in rather than fetched here, so it comes from the
# same cache as the stock being compared and covers the same calendar window
def compare_to_benchmark(stock_data, benchmark_data):
    benchmark_return = total_return(benchmark_data)
    benchmark_sharpe = sharpe_ratio(benchmark_data)

    stock_return = total_return(stock_data)
    stock_sharpe = sharpe_ratio(stock_data)

    return {
        'Benchmark Total Return': benchmark_return,
        'Benchmark Sharpe Ratio': benchmark_sharpe,
        'Stock Total Return': stock_return,
        'Stock Sharpe Ratio': stock_sharpe,
        'Beats Benchmark Return': stock_return > benchmark_return,
        'Beats Sharpe Ratio': stock_sharpe > benchmark_sharpe
    }