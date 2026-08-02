import yfinance as yf
import matplotlib.pyplot as plt

data = yf.Ticker('AAPL').history(period='5y')

plt.plot(data.index, data['Close'])
plt.title('AAPL Closing Price')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.savefig('chart.png')