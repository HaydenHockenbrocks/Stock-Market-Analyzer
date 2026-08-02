import yfinance as yf

ticker = yf.Ticker('AAPL')
data = ticker.history(period='5y')
data['Daily Return'] = data['Close'].pct_change()

positive = data[data['Daily Return'] > 0]
negative = data[data['Daily Return'] < 0]

print(f'It was positive for {len(positive)} days and negative for {len(negative)} days.')
print(f'The average daily return on positive days was {positive["Daily Return"].mean():.2f}')
print(f'The average daily return on negative days was {negative["Daily Return"].mean():.2f}')


