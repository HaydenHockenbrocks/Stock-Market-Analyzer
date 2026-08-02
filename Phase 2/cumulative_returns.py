import yfinance as yf
import matplotlib.pyplot as plt

data = yf.Ticker('AAPL').history(period='5y')

data['Daily Return'] = data['Close'].pct_change()
data['Cumulative Return'] = (1 + data['Daily Return']).cumprod()

plt.plot(data.index, data['Cumulative Return'])
plt.title('AAPL Cumulative Return')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.savefig('chart.png')

final = data['Cumulative Return'].iloc[-1] - 1
final = final * 100
print(f'The cumulative return over the last 5 years was {final:.2f}%')