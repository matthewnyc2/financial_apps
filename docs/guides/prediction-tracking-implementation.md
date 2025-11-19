# Prediction Tracking and Result Comparison Implementation Guide

**Purpose:** Practical implementation guide for storing trading predictions, tracking actual results, and comparing performance over time.

---

## Quick Reference

**Recommended Stack:**
- **Database:** PostgreSQL 15+ with TimescaleDB extension
- **ORM:** SQLAlchemy 2.0+
- **Analytics:** pandas, numpy
- **Visualization:** plotly or matplotlib

---

## 1. Database Schema

### 1.1 Complete Schema SQL

```sql
-- =====================================================
-- PREDICTIONS TABLE
-- =====================================================
CREATE TABLE predictions (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- Timestamp and identifiers
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '1m', '5m', '1h', '1d', etc.

    -- Prediction details
    prediction_type VARCHAR(20) NOT NULL, -- 'long', 'short', 'neutral', 'close'
    signal_strength DECIMAL(5,4) CHECK (signal_strength >= 0 AND signal_strength <= 1),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Price predictions
    current_price DECIMAL(18,8) NOT NULL,
    predicted_direction INTEGER, -- 1 (up), 0 (flat), -1 (down)
    predicted_return DECIMAL(10,6), -- Expected return percentage
    predicted_entry_price DECIMAL(18,8),
    predicted_exit_price DECIMAL(18,8),
    predicted_stop_loss DECIMAL(18,8),
    predicted_take_profit DECIMAL(18,8),

    -- Time predictions
    predicted_holding_period_minutes INTEGER,
    predicted_exit_time TIMESTAMPTZ,

    -- Risk/reward
    predicted_risk_reward_ratio DECIMAL(10,4),
    predicted_win_probability DECIMAL(5,4),

    -- Context and features
    features JSONB, -- All input features used for prediction
    market_conditions JSONB, -- Market state at time of prediction
    indicators JSONB, -- Technical indicator values

    -- Model metadata
    model_version VARCHAR(50),
    model_type VARCHAR(50), -- 'ml', 'rule_based', 'hybrid'
    backtest_sharpe DECIMAL(10,6), -- Strategy's backtest Sharpe at time of prediction

    -- Execution metadata
    environment VARCHAR(20) NOT NULL, -- 'backtest', 'paper', 'live'
    execution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executed', 'cancelled', 'failed'

    -- Notes
    notes TEXT
);

-- Indexes for performance
CREATE INDEX idx_predictions_timestamp ON predictions (timestamp DESC);
CREATE INDEX idx_predictions_strategy ON predictions (strategy_id, timestamp DESC);
CREATE INDEX idx_predictions_symbol ON predictions (symbol, timestamp DESC);
CREATE INDEX idx_predictions_status ON predictions (execution_status, timestamp DESC);
CREATE INDEX idx_predictions_environment ON predictions (environment, timestamp DESC);

-- Composite indexes for common queries
CREATE INDEX idx_predictions_strategy_symbol ON predictions (strategy_id, symbol, timestamp DESC);

-- Convert to TimescaleDB hypertable for better time-series performance
SELECT create_hypertable('predictions', 'timestamp',
    chunk_time_interval => INTERVAL '1 week');

-- =====================================================
-- ACTUAL RESULTS TABLE
-- =====================================================
CREATE TABLE actual_results (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- Link to prediction
    prediction_id BIGINT REFERENCES predictions(id) ON DELETE CASCADE,

    -- Timing
    entry_time TIMESTAMPTZ,
    exit_time TIMESTAMPTZ,
    duration_seconds INTEGER GENERATED ALWAYS AS
        (EXTRACT(EPOCH FROM (exit_time - entry_time))) STORED,
    duration_minutes DECIMAL(10,2) GENERATED ALWAYS AS
        (EXTRACT(EPOCH FROM (exit_time - entry_time)) / 60.0) STORED,

    -- Actual execution prices
    actual_entry_price DECIMAL(18,8),
    actual_exit_price DECIMAL(18,8),
    actual_stop_loss DECIMAL(18,8),
    actual_take_profit DECIMAL(18,8),

    -- Position details
    position_size DECIMAL(18,8),
    position_value DECIMAL(18,8),
    leverage DECIMAL(5,2) DEFAULT 1.0,

    -- Results
    gross_pnl DECIMAL(18,8),
    fees DECIMAL(18,8),
    slippage DECIMAL(18,8), -- Difference from expected execution price
    net_pnl DECIMAL(18,8),
    pnl_percent DECIMAL(10,6),
    pnl_points DECIMAL(18,8), -- Price points gained/lost

    -- Risk metrics
    actual_risk_reward_ratio DECIMAL(10,4),
    mae DECIMAL(18,8), -- Maximum Adverse Excursion
    mfe DECIMAL(18,8), -- Maximum Favorable Excursion

    -- Exit details
    exit_reason VARCHAR(50), -- 'target', 'stop_loss', 'timeout', 'manual', 'trailing_stop'
    exit_type VARCHAR(20), -- 'planned', 'forced', 'emergency'

    -- Market conditions at exit
    exit_market_conditions JSONB,

    -- Trade quality metrics
    slippage_bps INTEGER, -- Slippage in basis points
    execution_quality_score DECIMAL(5,4), -- 0-1 score for execution quality

    -- Notes
    notes TEXT
);

-- Indexes
CREATE INDEX idx_results_prediction ON actual_results (prediction_id);
CREATE INDEX idx_results_exit_time ON actual_results (exit_time DESC);
CREATE INDEX idx_results_exit_reason ON actual_results (exit_reason);
CREATE INDEX idx_results_pnl ON actual_results (net_pnl DESC);

-- =====================================================
-- PERFORMANCE SUMMARY TABLE
-- =====================================================
CREATE TABLE strategy_performance (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- Timestamp and identifiers
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20), -- NULL for aggregate across all symbols

    -- Period definition
    period_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'all_time'
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Environment
    environment VARCHAR(20) NOT NULL, -- 'backtest', 'paper', 'live'

    -- Return metrics
    gross_return DECIMAL(18,8),
    net_return DECIMAL(18,8),
    gross_return_pct DECIMAL(10,6),
    net_return_pct DECIMAL(10,6),
    annualized_return DECIMAL(10,6),

    -- Risk metrics
    sharpe_ratio DECIMAL(10,6),
    sortino_ratio DECIMAL(10,6),
    calmar_ratio DECIMAL(10,6),
    omega_ratio DECIMAL(10,6),
    max_drawdown DECIMAL(10,6),
    max_drawdown_duration_days INTEGER,
    avg_drawdown DECIMAL(10,6),
    volatility DECIMAL(10,6),
    downside_volatility DECIMAL(10,6),

    -- Trade statistics
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    breakeven_trades INTEGER,
    win_rate DECIMAL(5,4),
    loss_rate DECIMAL(5,4),

    -- Profit statistics
    profit_factor DECIMAL(10,6),
    avg_win DECIMAL(18,8),
    avg_loss DECIMAL(18,8),
    avg_win_pct DECIMAL(10,6),
    avg_loss_pct DECIMAL(10,6),
    largest_win DECIMAL(18,8),
    largest_loss DECIMAL(18,8),
    expectancy DECIMAL(18,8),

    -- Trade duration
    avg_winning_duration_minutes DECIMAL(10,2),
    avg_losing_duration_minutes DECIMAL(10,2),
    avg_trade_duration_minutes DECIMAL(10,2),

    -- Execution quality
    avg_slippage DECIMAL(18,8),
    avg_slippage_bps INTEGER,
    total_fees DECIMAL(18,8),

    -- Capital metrics
    starting_capital DECIMAL(18,8),
    ending_capital DECIMAL(18,8),
    peak_capital DECIMAL(18,8),
    current_drawdown_pct DECIMAL(10,6),

    -- Consistency metrics
    winning_months INTEGER,
    losing_months INTEGER,
    best_month_return DECIMAL(10,6),
    worst_month_return DECIMAL(10,6),

    -- Prediction accuracy (for ML strategies)
    total_predictions INTEGER,
    correct_predictions INTEGER,
    prediction_accuracy DECIMAL(5,4),

    -- Additional metrics in JSONB for flexibility
    additional_metrics JSONB
);

-- Indexes
CREATE INDEX idx_performance_strategy ON strategy_performance (strategy_id, timestamp DESC);
CREATE INDEX idx_performance_period ON strategy_performance (period_type, period_start DESC);
CREATE INDEX idx_performance_environment ON strategy_performance (environment, timestamp DESC);

-- Convert to hypertable
SELECT create_hypertable('strategy_performance', 'timestamp',
    chunk_time_interval => INTERVAL '1 month');

-- =====================================================
-- EQUITY CURVE TABLE
-- =====================================================
CREATE TABLE equity_curves (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- Timestamp and identifiers
    timestamp TIMESTAMPTZ NOT NULL,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20), -- NULL for aggregate

    -- Environment
    environment VARCHAR(20) NOT NULL,

    -- Account values
    equity DECIMAL(18,8) NOT NULL,
    cash DECIMAL(18,8),
    position_value DECIMAL(18,8),

    -- Returns
    daily_pnl DECIMAL(18,8),
    daily_return DECIMAL(10,6),
    cumulative_return DECIMAL(10,6),

    -- Drawdown tracking
    peak_equity DECIMAL(18,8),
    drawdown DECIMAL(10,6),
    drawdown_from_peak DECIMAL(10,6),
    underwater_days INTEGER, -- Consecutive days below peak

    -- Rolling metrics (30-day window)
    rolling_sharpe_30d DECIMAL(10,6),
    rolling_volatility_30d DECIMAL(10,6),
    rolling_win_rate_30d DECIMAL(5,4),

    -- Position metrics
    active_positions INTEGER,
    total_exposure DECIMAL(18,8)
);

-- Indexes
CREATE INDEX idx_equity_timestamp ON equity_curves (timestamp DESC);
CREATE INDEX idx_equity_strategy ON equity_curves (strategy_id, timestamp DESC);

-- Convert to hypertable
SELECT create_hypertable('equity_curves', 'timestamp',
    chunk_time_interval => INTERVAL '1 day');

-- =====================================================
-- PREDICTION ACCURACY TRACKING
-- =====================================================
CREATE TABLE prediction_accuracy (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- Reference
    prediction_id BIGINT REFERENCES predictions(id),
    result_id BIGINT REFERENCES actual_results(id),

    -- Accuracy metrics
    direction_correct BOOLEAN,
    return_error DECIMAL(10,6), -- predicted_return - actual_return
    return_error_abs DECIMAL(10,6),
    return_error_pct DECIMAL(10,6),

    price_error DECIMAL(18,8),
    price_error_pct DECIMAL(10,6),

    time_error_minutes INTEGER, -- predicted_duration - actual_duration

    -- Confidence calibration
    confidence_bucket VARCHAR(20), -- '0-20%', '20-40%', etc.
    confidence_vs_outcome DECIMAL(10,6) -- How well confidence predicted success
);

-- Indexes
CREATE INDEX idx_accuracy_prediction ON prediction_accuracy (prediction_id);
CREATE INDEX idx_accuracy_confidence ON prediction_accuracy (confidence_bucket);

-- =====================================================
-- BACKTESTS TABLE
-- =====================================================
CREATE TABLE backtests (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- Metadata
    run_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    strategy_id VARCHAR(50) NOT NULL,
    strategy_version VARCHAR(50),

    -- Test period
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    total_days INTEGER,

    -- Test type
    test_type VARCHAR(50) NOT NULL, -- 'in_sample', 'out_of_sample', 'walk_forward', 'monte_carlo'
    optimization_method VARCHAR(50), -- 'grid_search', 'genetic', 'bayesian', 'none'

    -- Parameters
    parameters JSONB NOT NULL,
    n_parameters INTEGER, -- Count of tunable parameters

    -- Data characteristics
    symbols_tested TEXT[], -- Array of symbols
    timeframe VARCHAR(10),
    data_source VARCHAR(100),
    total_bars INTEGER,

    -- Results summary
    total_return DECIMAL(10,6),
    annualized_return DECIMAL(10,6),
    sharpe_ratio DECIMAL(10,6),
    sortino_ratio DECIMAL(10,6),
    calmar_ratio DECIMAL(10,6),
    max_drawdown DECIMAL(10,6),
    win_rate DECIMAL(5,4),
    profit_factor DECIMAL(10,6),
    total_trades INTEGER,

    -- Monte Carlo results (if applicable)
    mc_simulations INTEGER,
    mc_median_return DECIMAL(10,6),
    mc_95th_pct_dd DECIMAL(10,6),
    mc_prob_profit DECIMAL(5,4),

    -- Overfitting metrics
    pbo_score DECIMAL(5,4), -- Probability of Backtest Overfitting
    deflated_sharpe DECIMAL(10,6),

    -- Storage
    results_file VARCHAR(255), -- Path to detailed results CSV/pickle
    equity_curve_file VARCHAR(255),
    trade_list_file VARCHAR(255),

    -- Environment
    python_version VARCHAR(20),
    framework VARCHAR(50), -- 'backtrader', 'vectorbt', etc.
    framework_version VARCHAR(20),

    -- Notes
    notes TEXT,
    tags TEXT[] -- For categorization
);

-- Indexes
CREATE INDEX idx_backtests_strategy ON backtests (strategy_id, run_timestamp DESC);
CREATE INDEX idx_backtests_type ON backtests (test_type, run_timestamp DESC);
CREATE INDEX idx_backtests_sharpe ON backtests (sharpe_ratio DESC);

-- =====================================================
-- USEFUL VIEWS
-- =====================================================

-- View: Latest strategy performance
CREATE VIEW v_latest_strategy_performance AS
SELECT DISTINCT ON (strategy_id, period_type)
    strategy_id,
    period_type,
    sharpe_ratio,
    max_drawdown,
    win_rate,
    total_trades,
    net_return_pct,
    timestamp
FROM strategy_performance
ORDER BY strategy_id, period_type, timestamp DESC;

-- View: Prediction accuracy by strategy
CREATE VIEW v_prediction_accuracy_by_strategy AS
SELECT
    p.strategy_id,
    p.environment,
    COUNT(*) as total_predictions,
    COUNT(pa.direction_correct) as predictions_with_results,
    SUM(CASE WHEN pa.direction_correct THEN 1 ELSE 0 END)::DECIMAL /
        NULLIF(COUNT(pa.direction_correct), 0) as direction_accuracy,
    AVG(ABS(pa.return_error)) as avg_return_error,
    AVG(pa.confidence_vs_outcome) as avg_confidence_calibration
FROM predictions p
LEFT JOIN prediction_accuracy pa ON p.id = pa.prediction_id
GROUP BY p.strategy_id, p.environment;

-- View: Trade quality metrics
CREATE VIEW v_trade_quality AS
SELECT
    p.strategy_id,
    p.symbol,
    COUNT(*) as total_trades,
    AVG(ar.slippage_bps) as avg_slippage_bps,
    AVG(ar.execution_quality_score) as avg_execution_quality,
    AVG(ar.fees) as avg_fees,
    AVG(ar.actual_risk_reward_ratio) as avg_risk_reward
FROM predictions p
JOIN actual_results ar ON p.id = ar.prediction_id
GROUP BY p.strategy_id, p.symbol;
```

### 1.2 Additional Useful Functions

```sql
-- Function: Calculate prediction accuracy
CREATE OR REPLACE FUNCTION calculate_prediction_accuracy(
    pred_id BIGINT,
    result_id BIGINT
) RETURNS VOID AS $$
DECLARE
    pred_return DECIMAL(10,6);
    actual_return DECIMAL(10,6);
    pred_direction INTEGER;
    actual_direction INTEGER;
BEGIN
    -- Get prediction details
    SELECT predicted_return, predicted_direction
    INTO pred_return, pred_direction
    FROM predictions
    WHERE id = pred_id;

    -- Get actual results
    SELECT pnl_percent, SIGN(pnl_percent)
    INTO actual_return, actual_direction
    FROM actual_results
    WHERE id = result_id;

    -- Insert accuracy record
    INSERT INTO prediction_accuracy (
        prediction_id,
        result_id,
        direction_correct,
        return_error,
        return_error_abs,
        return_error_pct
    ) VALUES (
        pred_id,
        result_id,
        pred_direction = actual_direction,
        pred_return - actual_return,
        ABS(pred_return - actual_return),
        CASE
            WHEN actual_return != 0 THEN
                ABS(pred_return - actual_return) / ABS(actual_return) * 100
            ELSE NULL
        END
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Update strategy performance
CREATE OR REPLACE FUNCTION update_strategy_performance(
    strat_id VARCHAR(50),
    period VARCHAR(20),
    env VARCHAR(20) DEFAULT 'live'
) RETURNS VOID AS $$
DECLARE
    period_start TIMESTAMPTZ;
    period_end TIMESTAMPTZ;
BEGIN
    -- Calculate period boundaries
    period_end := NOW();
    period_start := CASE period
        WHEN 'daily' THEN period_end - INTERVAL '1 day'
        WHEN 'weekly' THEN period_end - INTERVAL '7 days'
        WHEN 'monthly' THEN period_end - INTERVAL '1 month'
        WHEN 'quarterly' THEN period_end - INTERVAL '3 months'
        WHEN 'yearly' THEN period_end - INTERVAL '1 year'
        ELSE period_end - INTERVAL '1 day'
    END;

    -- Insert/update performance record
    INSERT INTO strategy_performance (
        strategy_id,
        period_type,
        period_start,
        period_end,
        environment,
        -- Calculate metrics from actual_results
        -- (simplified - full implementation would calculate all metrics)
        total_trades,
        winning_trades,
        win_rate,
        net_return
    )
    SELECT
        strat_id,
        period,
        period_start,
        period_end,
        env,
        COUNT(*),
        SUM(CASE WHEN ar.net_pnl > 0 THEN 1 ELSE 0 END),
        SUM(CASE WHEN ar.net_pnl > 0 THEN 1 ELSE 0 END)::DECIMAL / COUNT(*),
        SUM(ar.net_pnl)
    FROM predictions p
    JOIN actual_results ar ON p.id = ar.prediction_id
    WHERE p.strategy_id = strat_id
    AND p.environment = env
    AND ar.exit_time BETWEEN period_start AND period_end;
END;
$$ LANGUAGE plpgsql;
```

---

## 2. Python Implementation

### 2.1 Database Manager Class

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

class TradingDatabase:
    """
    Manages all database operations for prediction and result tracking
    """

    def __init__(self, connection_string):
        """
        Initialize database connection

        Args:
            connection_string: PostgreSQL connection string
                e.g., "postgresql://user:pass@localhost:5432/trading"
        """
        self.engine = create_engine(
            connection_string,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        self.Session = sessionmaker(bind=self.engine)

    # ===== PREDICTION STORAGE =====

    def store_prediction(self, prediction):
        """
        Store a trading prediction

        Args:
            prediction: Dict with prediction details

        Returns:
            prediction_id: Integer ID of stored prediction
        """
        with self.Session() as session:
            result = session.execute(
                text("""
                    INSERT INTO predictions (
                        timestamp, strategy_id, symbol, timeframe,
                        prediction_type, signal_strength, confidence_score,
                        current_price, predicted_direction, predicted_return,
                        predicted_entry_price, predicted_exit_price,
                        predicted_stop_loss, predicted_take_profit,
                        features, market_conditions, indicators,
                        model_version, model_type, environment
                    ) VALUES (
                        :timestamp, :strategy_id, :symbol, :timeframe,
                        :prediction_type, :signal_strength, :confidence_score,
                        :current_price, :predicted_direction, :predicted_return,
                        :predicted_entry_price, :predicted_exit_price,
                        :predicted_stop_loss, :predicted_take_profit,
                        :features, :market_conditions, :indicators,
                        :model_version, :model_type, :environment
                    )
                    RETURNING id
                """),
                {
                    'timestamp': prediction.get('timestamp', datetime.now()),
                    'strategy_id': prediction['strategy_id'],
                    'symbol': prediction['symbol'],
                    'timeframe': prediction.get('timeframe', '1d'),
                    'prediction_type': prediction['prediction_type'],
                    'signal_strength': prediction.get('signal_strength'),
                    'confidence_score': prediction.get('confidence_score'),
                    'current_price': prediction['current_price'],
                    'predicted_direction': prediction.get('predicted_direction'),
                    'predicted_return': prediction.get('predicted_return'),
                    'predicted_entry_price': prediction.get('predicted_entry_price'),
                    'predicted_exit_price': prediction.get('predicted_exit_price'),
                    'predicted_stop_loss': prediction.get('predicted_stop_loss'),
                    'predicted_take_profit': prediction.get('predicted_take_profit'),
                    'features': json.dumps(prediction.get('features', {})),
                    'market_conditions': json.dumps(prediction.get('market_conditions', {})),
                    'indicators': json.dumps(prediction.get('indicators', {})),
                    'model_version': prediction.get('model_version'),
                    'model_type': prediction.get('model_type'),
                    'environment': prediction.get('environment', 'live')
                }
            )
            prediction_id = result.fetchone()[0]
            session.commit()
            return prediction_id

    # ===== RESULT STORAGE =====

    def store_result(self, result):
        """
        Store actual trade result

        Args:
            result: Dict with result details including prediction_id

        Returns:
            result_id: Integer ID of stored result
        """
        with self.Session() as session:
            res = session.execute(
                text("""
                    INSERT INTO actual_results (
                        prediction_id, entry_time, exit_time,
                        actual_entry_price, actual_exit_price,
                        actual_stop_loss, actual_take_profit,
                        position_size, position_value, leverage,
                        gross_pnl, fees, slippage, net_pnl, pnl_percent,
                        exit_reason, exit_type,
                        mae, mfe, slippage_bps
                    ) VALUES (
                        :prediction_id, :entry_time, :exit_time,
                        :actual_entry_price, :actual_exit_price,
                        :actual_stop_loss, :actual_take_profit,
                        :position_size, :position_value, :leverage,
                        :gross_pnl, :fees, :slippage, :net_pnl, :pnl_percent,
                        :exit_reason, :exit_type,
                        :mae, :mfe, :slippage_bps
                    )
                    RETURNING id
                """),
                {
                    'prediction_id': result['prediction_id'],
                    'entry_time': result['entry_time'],
                    'exit_time': result['exit_time'],
                    'actual_entry_price': result['actual_entry_price'],
                    'actual_exit_price': result['actual_exit_price'],
                    'actual_stop_loss': result.get('actual_stop_loss'),
                    'actual_take_profit': result.get('actual_take_profit'),
                    'position_size': result['position_size'],
                    'position_value': result['position_value'],
                    'leverage': result.get('leverage', 1.0),
                    'gross_pnl': result['gross_pnl'],
                    'fees': result.get('fees', 0),
                    'slippage': result.get('slippage', 0),
                    'net_pnl': result['net_pnl'],
                    'pnl_percent': result['pnl_percent'],
                    'exit_reason': result['exit_reason'],
                    'exit_type': result.get('exit_type', 'planned'),
                    'mae': result.get('mae'),
                    'mfe': result.get('mfe'),
                    'slippage_bps': result.get('slippage_bps')
                }
            )
            result_id = res.fetchone()[0]
            session.commit()

            # Calculate prediction accuracy
            self._calculate_accuracy(result['prediction_id'], result_id)

            return result_id

    def _calculate_accuracy(self, prediction_id, result_id):
        """Calculate and store prediction accuracy"""
        with self.Session() as session:
            session.execute(
                text("SELECT calculate_prediction_accuracy(:pred_id, :res_id)"),
                {'pred_id': prediction_id, 'res_id': result_id}
            )
            session.commit()

    # ===== EQUITY CURVE TRACKING =====

    def update_equity_curve(self, strategy_id, equity_data, environment='live'):
        """
        Update equity curve with latest values

        Args:
            strategy_id: Strategy identifier
            equity_data: Dict with equity, cash, position_value, etc.
            environment: 'backtest', 'paper', or 'live'
        """
        with self.Session() as session:
            session.execute(
                text("""
                    INSERT INTO equity_curves (
                        timestamp, strategy_id, environment,
                        equity, cash, position_value,
                        daily_pnl, daily_return
                    ) VALUES (
                        :timestamp, :strategy_id, :environment,
                        :equity, :cash, :position_value,
                        :daily_pnl, :daily_return
                    )
                """),
                {
                    'timestamp': equity_data.get('timestamp', datetime.now()),
                    'strategy_id': strategy_id,
                    'environment': environment,
                    'equity': equity_data['equity'],
                    'cash': equity_data.get('cash'),
                    'position_value': equity_data.get('position_value'),
                    'daily_pnl': equity_data.get('daily_pnl'),
                    'daily_return': equity_data.get('daily_return')
                }
            )
            session.commit()

    # ===== PERFORMANCE QUERIES =====

    def get_prediction_accuracy(self, strategy_id, days=90, environment='live'):
        """
        Get prediction accuracy statistics

        Args:
            strategy_id: Strategy identifier
            days: Number of days to analyze
            environment: Which environment to analyze

        Returns:
            Dict with accuracy metrics
        """
        query = """
            SELECT
                COUNT(*) as total_predictions,
                COUNT(pa.direction_correct) as evaluated_predictions,
                SUM(CASE WHEN pa.direction_correct THEN 1 ELSE 0 END)::DECIMAL /
                    NULLIF(COUNT(pa.direction_correct), 0) as direction_accuracy,
                AVG(ABS(pa.return_error)) as avg_return_error,
                AVG(ar.net_pnl) as avg_pnl,
                STDDEV(ar.pnl_percent) as return_volatility,
                SUM(CASE WHEN ar.net_pnl > 0 THEN 1 ELSE 0 END)::DECIMAL /
                    NULLIF(COUNT(ar.net_pnl), 0) as win_rate
            FROM predictions p
            LEFT JOIN prediction_accuracy pa ON p.id = pa.prediction_id
            LEFT JOIN actual_results ar ON p.id = ar.prediction_id
            WHERE p.strategy_id = :strategy_id
            AND p.environment = :environment
            AND p.timestamp >= NOW() - INTERVAL ':days days'
        """

        with self.Session() as session:
            result = session.execute(
                text(query),
                {
                    'strategy_id': strategy_id,
                    'environment': environment,
                    'days': days
                }
            ).fetchone()

            if result and result[0] > 0:
                return {
                    'total_predictions': int(result[0]),
                    'evaluated_predictions': int(result[1]) if result[1] else 0,
                    'direction_accuracy': float(result[2]) if result[2] else 0,
                    'avg_return_error': float(result[3]) if result[3] else 0,
                    'avg_pnl': float(result[4]) if result[4] else 0,
                    'return_volatility': float(result[5]) if result[5] else 0,
                    'win_rate': float(result[6]) if result[6] else 0
                }
            else:
                return {
                    'total_predictions': 0,
                    'evaluated_predictions': 0,
                    'direction_accuracy': 0,
                    'avg_return_error': 0,
                    'avg_pnl': 0,
                    'return_volatility': 0,
                    'win_rate': 0
                }

    def get_equity_curve(self, strategy_id, days=None, environment='live'):
        """
        Retrieve equity curve

        Args:
            strategy_id: Strategy identifier
            days: Number of days (None for all)
            environment: Which environment

        Returns:
            pandas DataFrame with equity curve
        """
        query = """
            SELECT
                timestamp,
                equity,
                daily_return,
                drawdown,
                rolling_sharpe_30d
            FROM equity_curves
            WHERE strategy_id = :strategy_id
            AND environment = :environment
        """

        if days:
            query += " AND timestamp >= NOW() - INTERVAL ':days days'"

        query += " ORDER BY timestamp ASC"

        with self.Session() as session:
            params = {'strategy_id': strategy_id, 'environment': environment}
            if days:
                params['days'] = days

            df = pd.read_sql(
                text(query),
                session.bind,
                params=params
            )
            return df

    def compare_strategies(self, strategy_ids, period='monthly', environment='live'):
        """
        Compare multiple strategies

        Args:
            strategy_ids: List of strategy IDs to compare
            period: Period type ('daily', 'weekly', 'monthly')
            environment: Which environment

        Returns:
            pandas DataFrame with comparison
        """
        query = """
            SELECT
                strategy_id,
                sharpe_ratio,
                sortino_ratio,
                max_drawdown,
                win_rate,
                total_trades,
                net_return_pct,
                profit_factor
            FROM strategy_performance
            WHERE strategy_id = ANY(:strategy_ids)
            AND period_type = :period
            AND environment = :environment
            ORDER BY timestamp DESC
            LIMIT :n_strategies
        """

        with self.Session() as session:
            df = pd.read_sql(
                text(query),
                session.bind,
                params={
                    'strategy_ids': strategy_ids,
                    'period': period,
                    'environment': environment,
                    'n_strategies': len(strategy_ids)
                }
            )
            return df

    def get_live_vs_backtest_comparison(self, strategy_id):
        """
        Compare live performance to backtest results

        Args:
            strategy_id: Strategy identifier

        Returns:
            Dict with comparison metrics
        """
        query = """
            WITH live_perf AS (
                SELECT
                    AVG(sharpe_ratio) as sharpe,
                    AVG(max_drawdown) as max_dd,
                    AVG(win_rate) as win_rate
                FROM strategy_performance
                WHERE strategy_id = :strategy_id
                AND environment = 'live'
                AND period_type = 'monthly'
            ),
            backtest_perf AS (
                SELECT
                    sharpe_ratio as sharpe,
                    max_drawdown as max_dd,
                    win_rate
                FROM backtests
                WHERE strategy_id = :strategy_id
                AND test_type = 'out_of_sample'
                ORDER BY run_timestamp DESC
                LIMIT 1
            )
            SELECT
                l.sharpe as live_sharpe,
                b.sharpe as backtest_sharpe,
                l.sharpe / NULLIF(b.sharpe, 0) as sharpe_retention,
                l.max_dd as live_max_dd,
                b.max_dd as backtest_max_dd,
                l.win_rate as live_win_rate,
                b.win_rate as backtest_win_rate
            FROM live_perf l, backtest_perf b
        """

        with self.Session() as session:
            result = session.execute(
                text(query),
                {'strategy_id': strategy_id}
            ).fetchone()

            if result:
                return {
                    'live_sharpe': float(result[0]) if result[0] else 0,
                    'backtest_sharpe': float(result[1]) if result[1] else 0,
                    'sharpe_retention_pct': float(result[2] * 100) if result[2] else 0,
                    'live_max_dd': float(result[3]) if result[3] else 0,
                    'backtest_max_dd': float(result[4]) if result[4] else 0,
                    'live_win_rate': float(result[5]) if result[5] else 0,
                    'backtest_win_rate': float(result[6]) if result[6] else 0
                }
            else:
                return None
```

### 2.2 Usage Examples

```python
# Initialize database
db = TradingDatabase('postgresql://user:pass@localhost/trading')

# ===== EXAMPLE 1: Store a prediction =====
prediction = {
    'strategy_id': 'momentum_v2',
    'symbol': 'AAPL',
    'timeframe': '1d',
    'prediction_type': 'long',
    'signal_strength': 0.85,
    'confidence_score': 0.78,
    'current_price': 175.50,
    'predicted_direction': 1,
    'predicted_return': 0.025,  # 2.5% expected
    'predicted_entry_price': 175.50,
    'predicted_exit_price': 179.90,
    'predicted_stop_loss': 172.00,
    'features': {
        'momentum_20': 0.15,
        'rsi_14': 62.5,
        'volume_ratio': 1.3
    },
    'market_conditions': {
        'trend': 'bullish',
        'volatility': 'normal'
    },
    'indicators': {
        'sma_50': 170.20,
        'sma_200': 165.80
    },
    'model_version': '2.1.0',
    'model_type': 'ml',
    'environment': 'live'
}

prediction_id = db.store_prediction(prediction)
print(f"Stored prediction with ID: {prediction_id}")

# ===== EXAMPLE 2: Store trade result =====
result = {
    'prediction_id': prediction_id,
    'entry_time': datetime(2025, 11, 19, 9, 30),
    'exit_time': datetime(2025, 11, 20, 15, 0),
    'actual_entry_price': 175.60,  # Slight slippage
    'actual_exit_price': 178.20,
    'position_size': 100,  # shares
    'position_value': 17560.00,
    'gross_pnl': 260.00,  # (178.20 - 175.60) * 100
    'fees': 2.00,
    'slippage': 10.00,  # 0.10 * 100
    'net_pnl': 248.00,
    'pnl_percent': 1.41,  # 248 / 17560
    'exit_reason': 'target',
    'exit_type': 'planned',
    'mae': -50.00,  # Maximum adverse excursion
    'mfe': 350.00,  # Maximum favorable excursion
    'slippage_bps': 5  # 5 basis points
}

result_id = db.store_result(result)
print(f"Stored result with ID: {result_id}")

# ===== EXAMPLE 3: Check prediction accuracy =====
accuracy = db.get_prediction_accuracy('momentum_v2', days=30)
print(f"\nPrediction Accuracy (Last 30 days):")
print(f"  Total Predictions: {accuracy['total_predictions']}")
print(f"  Direction Accuracy: {accuracy['direction_accuracy']:.2%}")
print(f"  Average Return Error: {accuracy['avg_return_error']:.2%}")
print(f"  Win Rate: {accuracy['win_rate']:.2%}")

# ===== EXAMPLE 4: Get equity curve =====
equity_df = db.get_equity_curve('momentum_v2', days=90)
print(f"\nEquity Curve Shape: {equity_df.shape}")

# ===== EXAMPLE 5: Compare strategies =====
comparison = db.compare_strategies(
    ['momentum_v2', 'mean_reversion_v1', 'ml_ensemble_v3'],
    period='monthly'
)
print(f"\nStrategy Comparison:\n{comparison}")

# ===== EXAMPLE 6: Live vs Backtest comparison =====
comparison = db.get_live_vs_backtest_comparison('momentum_v2')
if comparison:
    print(f"\nLive vs Backtest Performance:")
    print(f"  Backtest Sharpe: {comparison['backtest_sharpe']:.2f}")
    print(f"  Live Sharpe: {comparison['live_sharpe']:.2f}")
    print(f"  Sharpe Retention: {comparison['sharpe_retention_pct']:.1f}%")
```

---

## 3. Automated Performance Reporting

### 3.1 Daily Report Generator

```python
from datetime import datetime, timedelta
import pandas as pd

class PerformanceReporter:
    """Generate automated performance reports"""

    def __init__(self, database):
        self.db = database

    def generate_daily_report(self, strategy_id, environment='live'):
        """Generate comprehensive daily performance report"""

        report = {
            'date': datetime.now().date(),
            'strategy_id': strategy_id,
            'environment': environment
        }

        # Get today's predictions and results
        report['predictions_today'] = self._get_todays_predictions(strategy_id)
        report['trades_closed_today'] = self._get_todays_closed_trades(strategy_id)

        # Get accuracy metrics
        report['accuracy_7d'] = self.db.get_prediction_accuracy(
            strategy_id, days=7, environment=environment
        )
        report['accuracy_30d'] = self.db.get_prediction_accuracy(
            strategy_id, days=30, environment=environment
        )

        # Get performance vs backtest
        report['vs_backtest'] = self.db.get_live_vs_backtest_comparison(strategy_id)

        # Get equity curve
        equity_df = self.db.get_equity_curve(strategy_id, days=30, environment=environment)
        if not equity_df.empty:
            report['current_equity'] = equity_df['equity'].iloc[-1]
            report['30d_return'] = (
                (equity_df['equity'].iloc[-1] / equity_df['equity'].iloc[0]) - 1
            ) * 100

        return report

    def _get_todays_predictions(self, strategy_id):
        """Get count of predictions made today"""
        with self.db.Session() as session:
            result = session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM predictions
                    WHERE strategy_id = :strategy_id
                    AND DATE(timestamp) = CURRENT_DATE
                """),
                {'strategy_id': strategy_id}
            ).fetchone()
            return result[0] if result else 0

    def _get_todays_closed_trades(self, strategy_id):
        """Get trades closed today"""
        with self.db.Session() as session:
            result = session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM predictions p
                    JOIN actual_results ar ON p.id = ar.prediction_id
                    WHERE p.strategy_id = :strategy_id
                    AND DATE(ar.exit_time) = CURRENT_DATE
                """),
                {'strategy_id': strategy_id}
            ).fetchone()
            return result[0] if result else 0

    def format_report(self, report):
        """Format report for email/console"""
        formatted = f"""
╔══════════════════════════════════════════════════════════════╗
║          DAILY TRADING PERFORMANCE REPORT                    ║
╠══════════════════════════════════════════════════════════════╣
║ Strategy: {report['strategy_id']:<47}║
║ Date: {report['date']:<51}║
║ Environment: {report['environment']:<44}║
╠══════════════════════════════════════════════════════════════╣
║ TODAY'S ACTIVITY                                              ║
╠══════════════════════════════════════════════════════════════╣
║ Predictions Made: {report['predictions_today']:<43}║
║ Trades Closed: {report['trades_closed_today']:<46}║
╠══════════════════════════════════════════════════════════════╣
║ 7-DAY ACCURACY                                                ║
╠══════════════════════════════════════════════════════════════╣
║ Total Predictions: {report['accuracy_7d']['total_predictions']:<42}║
║ Direction Accuracy: {report['accuracy_7d']['direction_accuracy']:<41.1%}║
║ Win Rate: {report['accuracy_7d']['win_rate']:<49.1%}║
╠══════════════════════════════════════════════════════════════╣
║ 30-DAY ACCURACY                                               ║
╠══════════════════════════════════════════════════════════════╣
║ Total Predictions: {report['accuracy_30d']['total_predictions']:<42}║
║ Direction Accuracy: {report['accuracy_30d']['direction_accuracy']:<40.1%}║
║ Win Rate: {report['accuracy_30d']['win_rate']:<49.1%}║
╠══════════════════════════════════════════════════════════════╣
║ LIVE VS BACKTEST                                              ║
╠══════════════════════════════════════════════════════════════╣
"""
        if report['vs_backtest']:
            formatted += f"""║ Backtest Sharpe: {report['vs_backtest']['backtest_sharpe']:<43.2f}║
║ Live Sharpe: {report['vs_backtest']['live_sharpe']:<47.2f}║
║ Retention: {report['vs_backtest']['sharpe_retention_pct']:<50.1f}%║
"""
        formatted += """╚══════════════════════════════════════════════════════════════╝
"""
        return formatted


# Usage
reporter = PerformanceReporter(db)
report = reporter.generate_daily_report('momentum_v2')
print(reporter.format_report(report))
```

---

## 4. Monitoring and Alerting

```python
class PerformanceMonitor:
    """Monitor strategy performance and send alerts"""

    def __init__(self, database, alert_thresholds=None):
        self.db = database
        self.thresholds = alert_thresholds or self._default_thresholds()

    def _default_thresholds(self):
        """Default alert thresholds"""
        return {
            'min_sharpe': 1.0,
            'max_drawdown': 0.15,  # 15%
            'min_win_rate': 0.50,  # 50%
            'min_accuracy': 0.55,  # 55%
            'max_degradation': 0.30  # 30% performance drop from backtest
        }

    def check_strategy_health(self, strategy_id, environment='live'):
        """
        Check if strategy is performing within acceptable ranges

        Returns:
            Dict with health status and any alerts
        """
        alerts = []

        # Get recent performance
        accuracy = self.db.get_prediction_accuracy(strategy_id, days=30, environment)
        comparison = self.db.get_live_vs_backtest_comparison(strategy_id)

        # Check win rate
        if accuracy['win_rate'] < self.thresholds['min_win_rate']:
            alerts.append({
                'level': 'WARNING',
                'metric': 'win_rate',
                'value': accuracy['win_rate'],
                'threshold': self.thresholds['min_win_rate'],
                'message': f"Win rate ({accuracy['win_rate']:.1%}) below threshold ({self.thresholds['min_win_rate']:.1%})"
            })

        # Check accuracy
        if accuracy['direction_accuracy'] < self.thresholds['min_accuracy']:
            alerts.append({
                'level': 'WARNING',
                'metric': 'direction_accuracy',
                'value': accuracy['direction_accuracy'],
                'threshold': self.thresholds['min_accuracy'],
                'message': f"Direction accuracy ({accuracy['direction_accuracy']:.1%}) below threshold"
            })

        # Check performance degradation
        if comparison:
            degradation = 1 - (comparison['sharpe_retention_pct'] / 100)
            if degradation > self.thresholds['max_degradation']:
                alerts.append({
                    'level': 'CRITICAL',
                    'metric': 'sharpe_degradation',
                    'value': degradation,
                    'threshold': self.thresholds['max_degradation'],
                    'message': f"Performance degraded {degradation:.1%} from backtest (threshold: {self.thresholds['max_degradation']:.1%})"
                })

        return {
            'strategy_id': strategy_id,
            'healthy': len(alerts) == 0,
            'alerts': alerts,
            'metrics': {
                'win_rate': accuracy['win_rate'],
                'direction_accuracy': accuracy['direction_accuracy'],
                'total_predictions': accuracy['total_predictions']
            }
        }

# Usage
monitor = PerformanceMonitor(db)
health = monitor.check_strategy_health('momentum_v2')

if not health['healthy']:
    print(f"⚠️ ALERTS for {health['strategy_id']}:")
    for alert in health['alerts']:
        print(f"  [{alert['level']}] {alert['message']}")
```

---

## Summary

This implementation guide provides:

1. **Complete Database Schema** - Production-ready tables for storing predictions, results, performance metrics, and equity curves
2. **Python Database Manager** - Full-featured class for all database operations
3. **Performance Reporting** - Automated daily/weekly/monthly reports
4. **Monitoring System** - Alert system for strategy health
5. **Comparison Tools** - Compare live vs backtest, strategy vs strategy

**Key Files Created:**
- `/home/user/financial_apps/docs/guides/backtesting-frameworks-research.md` - Comprehensive research on backtesting frameworks and methodologies
- `/home/user/financial_apps/docs/guides/prediction-tracking-implementation.md` - This implementation guide

**Next Steps:**
1. Set up PostgreSQL with TimescaleDB extension
2. Run the schema creation SQL
3. Implement the Python classes in your project
4. Integrate with your existing trading strategies
5. Start tracking predictions and results!
