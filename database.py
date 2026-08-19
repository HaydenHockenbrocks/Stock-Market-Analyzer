import sqlite3
from datetime import date as dt_date, datetime, timedelta

import pandas as pd

DB_PATH = 'stock_data.db'


# creates the three tables if they don't already exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            ticker TEXT NOT NULL,
            run_date TEXT NOT NULL,
            total_return REAL,
            volatility REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            PRIMARY KEY (ticker, run_date)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_results (
            ticker TEXT NOT NULL,
            run_date TEXT NOT NULL,
            strategy_name TEXT NOT NULL,
            cumulative_return REAL,
            pct_days_in_market REAL,
            PRIMARY KEY (ticker, run_date, strategy_name)
        )
    ''')

    conn.commit()
    conn.close()


# writes one row per trading day into the prices table
def save_prices(ticker, stock_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for date, row in stock_data.iterrows():
        date_str = date.strftime('%Y-%m-%d')

        cursor.execute('''
            INSERT OR REPLACE INTO prices (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, date_str, row['Open'], row['High'], row['Low'],
              row['Close'], row['Volume']))

    conn.commit()
    conn.close()


# reads prices back out, shaped like get_stock_data's output
def load_prices(ticker, start_date=None):
    conn = sqlite3.connect(DB_PATH)

    if start_date:
        query = 'SELECT * FROM prices WHERE ticker = ? AND date >= ? ORDER BY date'
        params = (ticker, start_date)
    else:
        query = 'SELECT * FROM prices WHERE ticker = ? ORDER BY date'
        params = (ticker,)

    df = pd.read_sql_query(query, conn, params=params,
                           index_col='date', parse_dates=['date'])
    conn.close()

    df = df.drop(columns=['ticker'])
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    # derived columns are recomputed on read rather than stored,
    # so they can't go stale if the calculation changes
    df['Daily Return'] = df['Close'].pct_change()
    df['Cumulative'] = (1 + df['Daily Return']).cumprod()

    return df


# how many rows we already hold for a ticker
def price_row_count(ticker):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM prices WHERE ticker = ?', (ticker,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


# most recent stored date for a ticker, or None if we hold nothing
def latest_stored_date(ticker):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM prices WHERE ticker = ?', (ticker,))
    result = cursor.fetchone()[0]
    conn.close()
    return result


# cache is usable if we hold enough rows and the newest one isn't stale.
# max_age_days is generous because markets close on weekends and holidays.
def has_fresh_data(ticker, min_rows=200, max_age_days=5):
    if price_row_count(ticker) < min_rows:
        return False

    latest = latest_stored_date(ticker)
    if latest is None:
        return False

    age = datetime.now() - datetime.strptime(latest, '%Y-%m-%d')
    return age <= timedelta(days=max_age_days)


# one row per ticker per analysis run
def save_metrics(ticker, metrics, run_date=None):
    if run_date is None:
        run_date = dt_date.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO metrics
        (ticker, run_date, total_return, volatility, sharpe_ratio, max_drawdown)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        ticker,
        run_date,
        metrics['Total Return'],
        metrics['Volatility'],
        metrics['Sharpe Ratio'],
        metrics['Max Drawdown']
    ))

    conn.commit()
    conn.close()


# one row per strategy per ticker per run
def save_backtest_result(ticker, strategy_name, cumulative_return,
                         pct_days_in_market, run_date=None):
    if run_date is None:
        run_date = dt_date.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO backtest_results
        (ticker, run_date, strategy_name, cumulative_return, pct_days_in_market)
        VALUES (?, ?, ?, ?, ?)
    ''', (ticker, run_date, strategy_name, cumulative_return, pct_days_in_market))

    conn.commit()
    conn.close()


# strategies ranked by return for one ticker, most recent run only
def strategy_leaderboard(ticker):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT strategy_name, cumulative_return, pct_days_in_market
        FROM backtest_results
        WHERE ticker = ?
          AND run_date = (SELECT MAX(run_date) FROM backtest_results WHERE ticker = ?)
        ORDER BY cumulative_return DESC
    ''', (ticker, ticker))

    rows = cursor.fetchall()
    conn.close()
    return rows


# each strategy averaged across every ticker, most recent run only
def strategy_averages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT strategy_name,
               AVG(cumulative_return) AS avg_return,
               AVG(pct_days_in_market) AS avg_exposure,
               COUNT(*) AS n_tickers
        FROM backtest_results
        WHERE run_date = (SELECT MAX(run_date) FROM backtest_results)
        GROUP BY strategy_name
        ORDER BY avg_return DESC
    ''')

    rows = cursor.fetchall()
    conn.close()
    return rows