import pandas as pd


# support functions
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
    # act on yesterday's signal, never today's
    stock_data['Strategy Return'] = stock_data['Daily Return'] * stock_data['Signal'].shift(1)
    return stock_data


def cumulative_return(stock_data):
    stock_data['Cumulative Return'] = (1 + stock_data['Strategy Return']).cumprod()
    return stock_data


def run_backtester(stock_data):
    generate_signals(stock_data)
    strategy_return(stock_data)
    cumulative_return(stock_data)
    return stock_data


# compares strategy against buy-and-hold over the same window.
# The first ~200 rows are excluded because the 200MA doesn't exist yet, which
# would otherwise force the strategy flat while buy-and-hold stays invested.
def backtester_summary(stock_data, stocks):
    final_data = {}

    for stock in stocks:
        df = stock_data[stock]
        valid = df[df['200MA'].notna()]

        strategy = (1 + valid['Strategy Return']).cumprod().iloc[-1]
        buy_hold = (1 + valid['Daily Return']).cumprod().iloc[-1]

        final_data[stock] = {
            'Strategy Return': strategy,
            'No Strategy Return': buy_hold,
            'Good Strategy': strategy > buy_hold,
            'Exposure': valid['Signal'].mean(),
        }

    return final_data