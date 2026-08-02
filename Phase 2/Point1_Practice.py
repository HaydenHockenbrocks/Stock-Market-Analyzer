import yfinance as yf
import matplotlib.pyplot as plt

ticker1 = yf.Ticker('AAPL').history(period='5y')
ticker2 = yf.Ticker('MSFT').history(period='5y')
ticker3 = yf.Ticker('TSLA').history(period='5y')

plt.plot(ticker1.index, ticker1['Close'], label='AAPL')
plt.plot(ticker2.index, ticker2['Close'], label='MSFT')
plt.plot(ticker3.index, ticker3['Close'], label='TSLA')
plt.title('AAPL, MSFT, and TSLA Closing Prices')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.savefig('chart.png')