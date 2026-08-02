import yfinance as yf
import matplotlib.pyplot as plt

data = yf.Ticker('AAPL').history(period='5y')

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

data['Daily Return'] = data['Close'].pct_change()
data['Cumulative Return'] = (1 + data['Daily Return']).cumprod()

ax1.plot (data.index, data['Close'])
ax1.set_title('AAPL Closing Price')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price')

ax2.plot(data.index, data['Cumulative Return'])
ax2.set_title('AAPL Cumulative Return')
ax2.set_xlabel('Date')
ax2.set_ylabel('Return')

ax3.plot(data.index, data['Daily Return'])
ax3.set_title('AAPL Daily Return')
ax3.set_xlabel('Date')
ax3.set_ylabel('Return')

plt.savefig('chart.png')