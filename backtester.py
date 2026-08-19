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


# Compares the crossover strategy against buy-and-hold over one shared window.
#
# Rows before the 200MA exists are always excluded: during warm-up the signal is
# forced to 0, so the strategy would sit in cash while buy-and-hold stays
# invested — a handicap imposed by data availability, not by any decision the
# strategy made.
#
# start_date optionally trims further. main.py passes the ML walk-forward start
# so that all four strategies are measured over identical calendar periods;
# comparing a 4.2-year compounded multiple against a 2.2-year one is meaningless.
def summarize_strategy(df, start_date=None):
    valid = df[df['200MA'].notna()]

    if start_date is not None:
        valid = valid[valid.index >= start_date]

    strategy = (1 + valid['Strategy Return']).cumprod().iloc[-1]
    buy_hold = (1 + valid['Daily Return']).cumprod().iloc[-1]

    return {
        'Strategy Return': strategy,
        'No Strategy Return': buy_hold,
        'Good Strategy': strategy > buy_hold,
        'Exposure': valid['Signal'].mean(),
        'n_days': len(valid),
        'start_date': valid.index[0],
    }


def backtester_summary(stock_data, stocks, start_dates=None):
    final_data = {}

    for stock in stocks:
        start = start_dates.get(stock) if start_dates else None
        final_data[stock] = summarize_strategy(stock_data[stock], start)

    return final_data