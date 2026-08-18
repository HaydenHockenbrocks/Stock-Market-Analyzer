import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from analyzer import *

FEATURES = ['50MA_ratio', '200MA_ratio', '5day_momentum',
            '10day_momentum', '10day_volatility', 'volume_change']


# builds all the input variables the models learn from
def build_features(stock_data):
    df = stock_data.copy()

    # moving averages relative to price
    df['50MA_ratio'] = df['Close'].rolling(50).mean() / df['Close']
    df['200MA_ratio'] = df['Close'].rolling(200).mean() / df['Close']

    # momentum
    df['5day_momentum'] = df['Close'].pct_change(5)
    df['10day_momentum'] = df['Close'].pct_change(10)

    # other
    df['10day_volatility'] = df['Daily Return'].rolling(10).std()
    df['volume_change'] = df['Volume'].pct_change()

    # target: 1 if tomorrow closes higher, 0 if not
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    df = df.dropna()

    return df


# fits both models on a given training slice
def fit_models(X_train, y_train):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train_scaled, y_train)

    rf_model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
    rf_model.fit(X_train_scaled, y_train)

    return lr_model, rf_model, scaler


# expanding-window walk-forward: train on the past, predict the near future, step forward
def walk_forward_predict(df, retrain_every=10, initial_train=500):
    X = df[FEATURES]
    y = df['Target']

    lr_preds = []
    rf_preds = []
    pred_index = []

    for start in range(initial_train, len(df), retrain_every):
        X_train = X.iloc[:start]
        y_train = y.iloc[:start]

        lr_model, rf_model, scaler = fit_models(X_train, y_train)

        X_future = X.iloc[start:start + retrain_every]
        X_future_scaled = scaler.transform(X_future)

        lr_preds.extend(lr_model.predict(X_future_scaled))
        rf_preds.extend(rf_model.predict(X_future_scaled))
        pred_index.extend(X_future.index)

    return lr_preds, rf_preds, pred_index


# backtests the walk-forward signals against buy-and-hold over the same window
def run_walk_forward_backtest(df, retrain_every=10, initial_train=500):
    lr_preds, rf_preds, pred_index = walk_forward_predict(df, retrain_every, initial_train)

    wf = df.loc[pred_index].copy()
    wf['lr_signal'] = lr_preds
    wf['rf_signal'] = rf_preds

    wf['lr_return'] = wf['Daily Return'] * wf['lr_signal'].shift(1)
    wf['rf_return'] = wf['Daily Return'] * wf['rf_signal'].shift(1)
    wf['lr_cumulative'] = (1 + wf['lr_return']).cumprod()
    wf['rf_cumulative'] = (1 + wf['rf_return']).cumprod()
    wf['buy_hold_cumulative'] = (1 + wf['Daily Return']).cumprod()

    return wf


# testing
data = get_stock_data('AAPL', '5y')
df = build_features(data)

wf = run_walk_forward_backtest(df)

print(f"LR strategy:  {wf['lr_cumulative'].iloc[-1]:.2f}x")
print(f"RF strategy:  {wf['rf_cumulative'].iloc[-1]:.2f}x")
print(f"Buy and hold: {wf['buy_hold_cumulative'].iloc[-1]:.2f}x")

print(f"LR in market: {wf['lr_signal'].mean():.1%} of days")
print(f"RF in market: {wf['rf_signal'].mean():.1%} of days")

lr_only = wf[(wf['lr_signal'] == 0) & (wf['rf_signal'] == 1)]
rf_only = wf[(wf['rf_signal'] == 0) & (wf['lr_signal'] == 1)]
print(f"Days only LR sat out: {len(lr_only)}, avg return those days: {lr_only['Daily Return'].mean():.3%}")
print(f"Days only RF sat out: {len(rf_only)}, avg return those days: {rf_only['Daily Return'].mean():.3%}")