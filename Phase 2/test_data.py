import yfinance as yf

ticker = yf.Ticker('AAPL')
data = ticker.history(period='1y')
print(data['Close'])
print(data['Close'].mean())
print(data['Close'].max())
print(data['Close'].min())