import yfinance as yf
import matplotlib.pyplot as plt
data = yf.Ticker('AAPL').history(period='5y')

data['20 Day MA'] = data['Close'].rolling(window=20).mean()
data['50 Day MA'] = data['Close'].rolling(window=50).mean()

plt.plot(data.index, data['Close'], label='Close Price')
plt.plot(data.index, data['20 Day MA'], label='20 Day MA')
plt.plot(data.index, data['50 Day MA'], label='50 Day MA')
plt.title('AAPL Rolling Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()