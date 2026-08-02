portfolio = {
    'AAPL': [0.12, 0.08, -0.03, 0.15, 0.07],
    'MSFT': [0.09, 0.11, 0.05, -0.02, 0.13],
    'TSLA': [0.25, -0.18, 0.40, -0.10, 0.30],
}

def test_ticker(ticker):
    if ticker.upper() in portfolio:
        return ticker
    else:
        print('Sorry, I do not recognize that ticker. Please try again.')
        print('What stock would you like to look at today?')
        return test_ticker(input())

def test_response(tick):
        return('Your average return is: ' + str(average(tick)) + '\n' + 'Your maximum return is: ' + str(maximum(tick)) + '\n' + 'Your minimum return is: ' + str(minimum(tick)))


def average(tick):
    return sum(portfolio[tick.upper()]) / len(portfolio[tick.upper()])

def maximum(tick):
    return max(portfolio[tick.upper()])

def minimum(tick):
    return min(portfolio[tick.upper()])




print('What stock would you like to look at today?')
tick = test_ticker(input())
with open('portfolio_summary.txt', 'w') as f:
    f.write(str(test_response(tick)))
 




