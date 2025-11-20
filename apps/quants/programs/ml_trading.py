"""
Machine Learning Trading System
Implements Random Forest, XGBoost with feature engineering and walk-forward validation.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor, XGBClassifier
import warnings

warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Technical indicator and feature engineering for trading."""

    def __init__(self, lookback_periods=[5, 10, 20, 50]):
        self.lookback_periods = lookback_periods

    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators from price data.

        Parameters:
        df: DataFrame with OHLCV data

        Returns:
        DataFrame with added technical indicators
        """
        df = df.copy()

        # Simple Moving Averages (SMA)
        for period in [5, 10, 20, 50, 200]:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()

        # Exponential Moving Average (EMA)
        for period in [12, 26]:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

        # RSI (Relative Strength Index)
        df['RSI'] = self._calculate_rsi(df['Close'])

        # MACD (Moving Average Convergence Divergence)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = self._calculate_macd(df['Close'])

        # Bollinger Bands
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self._calculate_bollinger_bands(df['Close'])

        # ATR (Average True Range)
        df['ATR'] = self._calculate_atr(df)

        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

        return df

    def calculate_lagged_returns(self, df, lags=[1, 2, 3, 5, 10]):
        """
        Calculate lagged returns as features.
        """
        df = df.copy()
        df['Returns'] = df['Close'].pct_change()

        for lag in lags:
            df[f'Returns_Lag_{lag}'] = df['Returns'].shift(lag)

        # Rolling volatility (standard deviation of returns)
        df['Volatility_20'] = df['Returns'].rolling(window=20).std()
        df['Volatility_50'] = df['Returns'].rolling(window=50).std()

        return df

    def calculate_momentum_features(self, df):
        """
        Calculate momentum-based features.
        """
        df = df.copy()

        # Rate of Change (ROC)
        for period in [12, 25]:
            df[f'ROC_{period}'] = df['Close'].pct_change(periods=period)

        # Stochastic Oscillator
        df['Stoch_%K'], df['Stoch_%D'] = self._calculate_stochastic(df)

        # Williams %R
        df['Williams_%R'] = self._calculate_williams_r(df)

        return df

    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def _calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD."""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist

    @staticmethod
    def _calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return upper, sma, lower

    @staticmethod
    def _calculate_atr(df, period=14):
        """Calculate Average True Range."""
        df = df.copy()
        df['tr1'] = df['High'] - df['Low']
        df['tr2'] = abs(df['High'] - df['Close'].shift())
        df['tr3'] = abs(df['Low'] - df['Close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        atr = df['tr'].rolling(window=period).mean()
        return atr

    @staticmethod
    def _calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3):
        """Calculate Stochastic Oscillator."""
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()
        k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        k_smooth = k.rolling(window=smooth_k).mean()
        d_smooth = k_smooth.rolling(window=smooth_d).mean()
        return k_smooth, d_smooth

    @staticmethod
    def _calculate_williams_r(df, period=14):
        """Calculate Williams %R."""
        high_max = df['High'].rolling(window=period).max()
        low_min = df['Low'].rolling(window=period).min()
        wr = -100 * ((high_max - df['Close']) / (high_max - low_min))
        return wr


class MLTradingModel:
    """Machine Learning models for trading prediction."""

    def __init__(self, model_type='rf_classifier', **kwargs):
        """
        Initialize ML model.

        Parameters:
        model_type: 'rf_classifier', 'rf_regressor', 'xgb_classifier', 'xgb_regressor'
        """
        self.model_type = model_type
        self.model = self._init_model(model_type, kwargs)
        self.scaler = StandardScaler()
        self.feature_names = None
        self.feature_importance = None

    def _init_model(self, model_type, kwargs):
        """Initialize the appropriate model."""
        if model_type == 'rf_classifier':
            return RandomForestClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 15),
                min_samples_split=kwargs.get('min_samples_split', 5),
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'rf_regressor':
            return RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 15),
                min_samples_split=kwargs.get('min_samples_split', 5),
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'xgb_classifier':
            return XGBClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 7),
                learning_rate=kwargs.get('learning_rate', 0.1),
                subsample=kwargs.get('subsample', 0.8),
                random_state=42,
                eval_metric='logloss'
            )
        elif model_type == 'xgb_regressor':
            return XGBRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 7),
                learning_rate=kwargs.get('learning_rate', 0.1),
                subsample=kwargs.get('subsample', 0.8),
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def prepare_features(self, df, feature_cols, target_col=None):
        """Prepare and scale features."""
        X = df[feature_cols].dropna()

        if target_col:
            y = df.loc[X.index, target_col]
            # Remove any remaining NaN
            valid_idx = ~y.isna()
            X = X[valid_idx]
            y = y[valid_idx]
            return X, y

        return X

    def train(self, X_train, y_train):
        """Train the model."""
        self.feature_names = X_train.columns.tolist()
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        self._compute_feature_importance(X_train.columns)

    def predict(self, X_test):
        """Make predictions."""
        X_scaled = self.scaler.transform(X_test)
        return self.model.predict(X_scaled)

    def predict_proba(self, X_test):
        """Get prediction probabilities (for classifiers)."""
        if 'classifier' not in self.model_type:
            raise ValueError("predict_proba only available for classifier models")
        X_scaled = self.scaler.transform(X_test)
        return self.model.predict_proba(X_scaled)

    def _compute_feature_importance(self, feature_names):
        """Compute and store feature importance."""
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)


class WalkForwardValidator:
    """Walk-forward cross-validation for time series."""

    def __init__(self, n_splits=10, train_size=None, test_size=None):
        """
        Initialize walk-forward validator.

        Parameters:
        n_splits: Number of splits
        train_size: Size of training window (None = growing)
        test_size: Size of test window
        """
        self.n_splits = n_splits
        self.train_size = train_size
        self.test_size = test_size
        self.splits = []

    def get_splits(self, n_samples):
        """Generate walk-forward split indices."""
        if self.test_size is None:
            self.test_size = n_samples // (self.n_splits + 1)

        if self.train_size is None:
            # Growing window
            for i in range(self.n_splits):
                train_end = n_samples - self.test_size * (self.n_splits - i)
                test_end = train_end + self.test_size
                self.splits.append((0, train_end, test_end))
        else:
            # Fixed window
            for i in range(self.n_splits):
                train_start = max(0, n_samples - self.train_size * (self.n_splits - i) - self.test_size * (self.n_splits - i))
                train_end = train_start + self.train_size
                test_end = train_end + self.test_size
                if test_end <= n_samples:
                    self.splits.append((train_start, train_end, test_end))

        return self.splits

    def backtest(self, df, feature_cols, target_col, model_type='xgb_regressor', **model_kwargs):
        """
        Perform walk-forward backtest.

        Returns:
        Dictionary with results
        """
        results = {
            'predictions': [],
            'actuals': [],
            'train_indices': [],
            'test_indices': [],
            'models': [],
            'feature_importances': []
        }

        splits = self.get_splits(len(df))

        for fold, (train_start, train_end, test_end) in enumerate(splits):
            print(f"Walk-forward fold {fold + 1}/{len(splits)}")

            # Prepare train and test data
            train_data = df.iloc[train_start:train_end]
            test_data = df.iloc[train_end:test_end]

            # Initialize model
            model = MLTradingModel(model_type=model_type, **model_kwargs)

            # Prepare features
            X_train, y_train = model.prepare_features(train_data, feature_cols, target_col)
            X_test, y_test = model.prepare_features(test_data, feature_cols, target_col)

            if len(X_train) == 0 or len(X_test) == 0:
                continue

            # Train model
            model.train(X_train, y_train)

            # Predict
            y_pred = model.predict(X_test)

            # Store results
            results['predictions'].extend(y_pred)
            results['actuals'].extend(y_test.values)
            results['models'].append(model)
            if model.feature_importance is not None:
                results['feature_importances'].append(model.feature_importance)
            results['train_indices'].append((train_start, train_end))
            results['test_indices'].append((train_end, test_end))

        return results


def create_trading_dataset(df):
    """
    Create complete trading dataset with all features.

    Parameters:
    df: DataFrame with OHLCV data (Open, High, Low, Close, Volume)

    Returns:
    DataFrame with features and target
    """
    # Feature engineering
    engineer = FeatureEngineer()

    df = engineer.calculate_technical_indicators(df)
    df = engineer.calculate_lagged_returns(df)
    df = engineer.calculate_momentum_features(df)

    # Create target: 1 if next day return > threshold, 0 otherwise
    threshold = 0.005  # 0.5% return threshold
    df['Target'] = (df['Returns'].shift(-1) > threshold).astype(int)

    # Drop NaN values
    df = df.dropna()

    return df


def get_feature_columns(df):
    """Get list of feature column names."""
    exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'Returns', 'Target', 'Date']
    feature_cols = [col for col in df.columns if col not in exclude]
    return feature_cols


# Example usage
if __name__ == "__main__":
    print("ML Trading System - Module loaded")
    print("Available classes:")
    print("  - FeatureEngineer: Technical indicators and feature engineering")
    print("  - MLTradingModel: Random Forest and XGBoost models")
    print("  - WalkForwardValidator: Time-series cross-validation")

    # Example: Create sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    data = {
        'Date': dates,
        'Open': 100 + np.cumsum(np.random.randn(500) * 0.5),
        'High': 102 + np.cumsum(np.random.randn(500) * 0.5),
        'Low': 98 + np.cumsum(np.random.randn(500) * 0.5),
        'Close': 100 + np.cumsum(np.random.randn(500) * 0.5),
        'Volume': np.random.randint(1000000, 10000000, 500)
    }

    sample_df = pd.DataFrame(data)
    sample_df = sample_df[sample_df['Low'] <= sample_df['Close']]
    sample_df = sample_df[sample_df['High'] >= sample_df['Close']]

    # Create dataset with features
    trading_df = create_trading_dataset(sample_df.reset_index(drop=True))
    feature_cols = get_feature_columns(trading_df)

    print(f"\nSample dataset created with {len(trading_df)} rows and {len(feature_cols)} features")
    print(f"Features: {feature_cols[:5]}... (showing first 5)")
