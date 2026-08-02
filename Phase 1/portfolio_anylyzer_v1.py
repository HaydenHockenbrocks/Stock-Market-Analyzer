portfolio = {
    'AAPL': [0.12, 0.08, -0.03, 0.15, 0.07],
    'MSFT': [0.09, 0.11, 0.05, -0.02, 0.13],
    'TSLA': [0.25, -0.18, 0.40, -0.10, 0.30],
    'GOOGL': [0.14, 0.07, -0.06, 0.18, 0.11],
    'AMZN': [0.20, 0.15, -0.10, 0.22, 0.08],
    'NVDA': [0.35, 0.28, -0.15, 0.45, 0.20],
    'JPM': [0.08, 0.06, -0.08, 0.10, 0.05],
    'JNJ': [0.04, 0.06, 0.03, -0.01, 0.05],
    'BRK': [0.07, 0.09, 0.02, 0.08, 0.06],
    'META': [0.30, -0.25, 0.50, 0.18, 0.12],
}

tickers = list(portfolio.keys())

def start():
    console_stocks()
    write_report()

def average(tick):
    anwser = sum(portfolio[tick.upper()]) / len(portfolio[tick.upper()])
    anwser = f'{anwser*100:.2f}'
    return anwser + '%'

def maximum(tick):
    anwser = max(portfolio[tick.upper()])
    anwser = f'{anwser*100:.2f}'
    return anwser + '%'

def minimum(tick):
    anwser = min(portfolio[tick.upper()])
    anwser = f'{anwser*100:.2f}'
    return anwser + '%'

def console_stocks():
    i = 0
    print('-----Stocks-----')
    while i < len(portfolio):
        test = tickers[i]
        print('Average: ' + str(average(test)) + ' | Maximum: ' + str(maximum(test)) + ' | Minimum: ' + str(minimum(test)))
        i += 1

def write_report():
    with open('portfolio_summary.txt', 'w') as f:
        f.write('-----Stocks-----\n')
        i=0
        while i < len(tickers):
            f.write('-----' + tickers[i] + '-----\n')
            f.write('Average: ' + str(average(tickers[i])) + '\nMaximum: ' + str(maximum(tickers[i])) + '\nMinimum: ' + str(minimum(tickers[i])) + '\n')
            i += 1

start()