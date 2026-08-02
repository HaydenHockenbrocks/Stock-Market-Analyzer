import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN']

ticker1 = yf.Ticker('AAPL').history(period='5y')['Close']
ticker2 = yf.Ticker('MSFT').history(period='5y')['Close']
ticker3 = yf.Ticker('TSLA').history(period='5y')['Close']
ticker4 = yf.Ticker('GOOGL').history(period='5y')['Close']
ticker5 = yf.Ticker('AMZN').history(period='5y')['Close']


closes = pd.concat([ticker1, ticker2, ticker3, ticker4, ticker5], axis=1)
closes.columns = tickers

returns = pd.concat([ticker1.pct_change(), ticker2.pct_change(), ticker3.pct_change(), ticker4.pct_change(), ticker5.pct_change()], axis=1)
returns.columns = tickers


cumulative = pd.concat([(1 + ticker1.pct_change()).cumprod(), (1 + ticker2.pct_change()).cumprod(), (1 + ticker3.pct_change()).cumprod(), (1 + ticker4.pct_change()).cumprod(), (1 + ticker5.pct_change()).cumprod()], axis=1)
cumulative.columns = tickers


for ticker in tickers:
    avg = returns[ticker].mean()
    vol = returns[ticker].std()
    com = cumulative[ticker].iloc[-1] - 1
    print(f'{ticker}: Average Daily Return = {avg:.4f}, Volatility = {vol:.4f}, Cumulative Return = {com:.2f}%')
    plt.plot(cumulative.index, cumulative[ticker], label=ticker)


plt.title('Cumulative Returns of AAPL, MSFT, TSLA, GOOGL, and AMZN')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.savefig('chart.png')

