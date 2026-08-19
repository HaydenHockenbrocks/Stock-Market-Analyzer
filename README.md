# Stock Market Analyzer

I created a Python tool that pulls live market data from yfinance, calculates portfolio metrics and backtests four different trading strategies against each other over identical windows.

## Key Findings

Across the 5 tickers that I analyzed over 555 out of sample trading days no strategy was able to beat a simple buy and hold strategy. This is likely related to the consistent Bull market over the past 5 years.

| Strategy | Avg. return | Avg. time in market |
|---|---|---|
| Buy and hold | 1.79x | 100% |
| Random forest | 1.63x | 84.9% |
| Logistic regression | 1.55x | 83.7% |
| 50/200 MA crossover | 1.44x | 85.2% |

This data demonstrates a strong relationship between the average time spent in the market and the average return. The strategies that sat out the most days generally performed worse, and the closer a strategy came to being fully invested, the closer its return came to buy and hold. A pattern like this shows that my strategies were not avoiding down days, simply missing out on up days that buy and hold was able to take advantage of.

The clearest case is JNJ, where logistic regression was invested only 45.7% of days and returned 1.70x against buy-and-hold's 1.97x. We were missing out on more gains than losses avoided.

## What my project does

- Pulls daily OHLCV data via yfinance for any set of stock tickers
- Computes total return, daily volatility, annualized sharpe ratio, and max drawdown
- Benchmarks each stock against VOO on both raw return and risk-adjusted return
- Backtests a 50/200-day moving average crossover strategy
- Trains logistic regression and random forest classifiers to predict next-day direction
- Caches all price data in SQLite so repeat runs don't rely on the API
- Generates comparison charts and a multi-page PDF summary

## Methodology

### Walk-forward validation

The machine learning strategies are validated with an expanded window walk forward model that is trained only on data available up to a given date. It works by testing it against the next 10 days, looping that data into the training set, and trying the next 10 after that. This results in every test being guaranteed to be out of sample.

This problem came up in an earlier version of my model where I planned to train on 80% of the data and then create prediction signals for every day. However, this resulted in the algorithm producing a 4.67x return for the random forest ML on AAPL. This number seemed too good to be true, and after implementing proper walk-forward validation the same model returned 1.27x. This proves that my algorithm was being tested on data it had already seen during training.

### Shared measurement window

Another issue that I came across when reviewing my code is that the moving average strategy was being tested and compared on a 1056 day window while the ML strategies were only being tested and compared on a 555 day window. This created a situation where the MA strategy was able to have a higher compounded return than the ML strategies, creating an improper comparison.

All four strategies are now trimmed to the same 555 day window. The `backtest_results` table stores `n_days` and `window_start` on every row, and a SQL check verifies that the windows line up each time the project runs.

## Setup

```
pip install -r requirements.txt
python3 main.py
```

The first run pulls from Yahoo Finance and fills the local SQLite database. After that, runs read from the cache unless the stored data is more than 5 days old.

The walk-forward backtest retrains roughly 56 model pairs per ticker and takes a few minutes. Set `RUN_ML = False` at the top of `main.py` to skip it.

## Structure

```
main.py           orchestration and reporting
analyzer.py       data fetching and portfolio metrics
backtester.py     moving average crossover strategy
ml_strategy.py    feature engineering, walk-forward ML
database.py       SQLite schema, persistence, queries
report.py         PDF generation
```

## Limitations

- **No transaction costs.** The ML strategies flip position frequently. While it is becoming more common for firms to offer fee free transactions this is still something that needs to be accounted for.
- **One market type.** The test window is a bull market. Timing strategies are very impractical when the market is consistently increasing. Results might be substantially different in a sideways or declining market.
- **Five tickers, one asset class.** Not a broad enough sample size.
- **Daily frequency only.** No mid-day data, and no fundamental or macro features.
