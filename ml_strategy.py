import warnings

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Accelerate BLAS on macOS raises spurious matmul warnings during LogisticRegression
# fitting. Verified with np.isfinite that every scaled training slice is finite,
# so these are a platform artifact rather than a data problem.
warnings.filterwarnings('ignore', category=RuntimeWarning, module='sklearn')

FEATURES = ['50MA_ratio', '200MA_ratio', '5day_momentum',
            '10day_momentum', '10day_volatility', 'volume_change']


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

    # Target is computed BEFORE truncating, so shift(-1) can still see the real
    # next-day close for every row that survives. Order matters here: truncating
    # first would leave the new last row unable to see its own tomorrow, and
    # NaN > x evaluates False rather than NaN, so it would be silently
    # mislabelled 0 instead of dropped.
    df['Target'] = (df['Close'].shift(-1) > df['Close'])

    # the true final row has no tomorrow at all; drop it rather than label it
    df = df.iloc[:-1].copy()
    df['Target'] = df['Target'].astype(int)

    # zero-volume days produce inf on pct_change, and dropna doesn't catch inf
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    return df


def fit_models(X_train, y_train):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train_scaled, y_train)

    rf_model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
    rf_model.fit(X_train_scaled, y_train)

    return lr_model, rf_model, scaler


# Expanding-window walk-forward: train only on the past, predict the near future,
# step forward. The scaler is re-fit on each training slice and only .transform()s
# the future block, so no future information reaches the model in any form.
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


def run_walk_forward_backtest(df, retrain_every=10, initial_train=500):
    lr_preds, rf_preds, pred_index = walk_forward_predict(df, retrain_every, initial_train)

    wf = df.loc[pred_index].copy()
    wf['lr_signal'] = lr_preds
    wf['rf_signal'] = rf_preds

    # act on yesterday's signal, never today's
    wf['lr_return'] = wf['Daily Return'] * wf['lr_signal'].shift(1)
    wf['rf_return'] = wf['Daily Return'] * wf['rf_signal'].shift(1)

    wf['lr_cumulative'] = (1 + wf['lr_return']).cumprod()
    wf['rf_cumulative'] = (1 + wf['rf_return']).cumprod()
    wf['buy_hold_cumulative'] = (1 + wf['Daily Return']).cumprod()

    return wf


# Runs the full ML pipeline for one stock and returns a flat summary.
# start_date is returned so main.py can trim the other strategies to the same
# window, keeping every cumulative return comparable.
def ml_summary(stock_data, retrain_every=10, initial_train=500):
    df = build_features(stock_data)

    if len(df) <= initial_train:
        return None

    wf = run_walk_forward_backtest(df, retrain_every, initial_train)

    return {
        'lr_return': wf['lr_cumulative'].iloc[-1],
        'rf_return': wf['rf_cumulative'].iloc[-1],
        'buy_hold_return': wf['buy_hold_cumulative'].iloc[-1],
        'lr_exposure': wf['lr_signal'].mean(),
        'rf_exposure': wf['rf_signal'].mean(),
        'base_rate': wf['Target'].mean(),
        'n_days': int(wf['lr_return'].notna().sum()),
        'start_date': wf.index[0],
    }


if __name__ == '__main__':
    from analyzer import get_stock_data

    data = get_stock_data('AAPL', '5y')
    results = ml_summary(data)

    print(f"Walk-forward window: {results['n_days']} days "
          f"starting {results['start_date'].date()}")
    print(f"Actual up days:      {results['base_rate']:.1%}\n")
    print(f"Buy and hold:  {results['buy_hold_return']:.2f}x")
    print(f"Random forest: {results['rf_return']:.2f}x  "
          f"(in market {results['rf_exposure']:.1%} of days)")
    print(f"Logistic reg:  {results['lr_return']:.2f}x  "
          f"(in market {results['lr_exposure']:.1%} of days)")