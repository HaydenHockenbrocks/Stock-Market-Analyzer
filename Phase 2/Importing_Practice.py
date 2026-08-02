import yfinance as yf

ticker = yf.Ticker('SWTSX')
data = ticker.history(period='5y')
data['Daily Return'] = data['Close'].pct_change()

print(data.head())
print(data.tail())

print('Average: ' + f'{data["Close"].mean():.2f}' + ' Max: ' + f'{data["Close"].max():.2f}' + ' Min: ' + f'{data["Close"].min():.2f}')
