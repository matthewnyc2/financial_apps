#!/usr/bin/env python3
"""
Opening Hour Stock Predictor - Main Application
Predicts stocks most likely to gain/lose value in the first trading hour.
"""

import sys
import os
import logging
import yaml
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data.data_acquisition import MultiSourceDataAcquirer, get_sp500_symbols, get_nasdaq100_symbols
from analysis.quantitative import QuantitativeAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpeningHourPredictor:
    """Main application class"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize the predictor"""
        self.config = self._load_config(config_path)
        self.data_acquirer = MultiSourceDataAcquirer(self.config)
        self.quant_analyzer = QuantitativeAnalyzer(self.config)

        logger.info("Opening Hour Predictor initialized")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Return default config
            return {
                'data': {'sources': ['yfinance'], 'max_download_workers': 50},
                'analysis': {'max_compute_workers': 8},
                'prediction': {'top_n_gainers': 10, 'top_n_losers': 10}
            }

    # ==================== DATA PIPELINE ====================

    def download_universe(self, universe: str = 'sp500') -> List[str]:
        """Download list of stocks to analyze"""
        logger.info(f"Fetching {universe} universe...")

        if universe == 'sp500':
            symbols = get_sp500_symbols()
        elif universe == 'nasdaq100':
            symbols = get_nasdaq100_symbols()
        elif universe == 'custom':
            # Load from file or user input
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA']  # Example
        else:
            logger.warning(f"Unknown universe: {universe}. Using S&P 500.")
            symbols = get_sp500_symbols()

        logger.info(f"Universe contains {len(symbols)} symbols")
        return symbols

    def download_historical_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Download historical data for all symbols"""
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=504)).strftime('%Y-%m-%d')  # 2 years
        interval = self.config.get('data', {}).get('intraday_interval', '5m')

        logger.info(f"Downloading data from {start_date} to {end_date}, interval={interval}")

        max_workers = self.config.get('data', {}).get('max_download_workers', 50)
        stock_data = self.data_acquirer.download_multiple_stocks(
            symbols, start_date, end_date, interval, max_workers
        )

        return stock_data

    def calculate_indicators(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Calculate technical indicators for all stocks"""
        logger.info("Calculating quantitative indicators...")
        analyzed_data = self.quant_analyzer.analyze_multiple_stocks(stock_data)
        return analyzed_data

    # ==================== PREDICTION (SIMPLIFIED) ====================

    def score_stocks(self, analyzed_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Score stocks based on opening hour criteria.
        This is a simplified scoring system. Full ML models would be in models/ directory.
        """
        logger.info("Scoring stocks for opening hour potential...")

        scores = []

        for symbol, df in analyzed_data.items():
            try:
                # Get latest metrics
                latest = self.quant_analyzer.get_latest_metrics(df)

                if not latest:
                    continue

                # Calculate opening hour score (simplified)
                score = 0
                reasons = []

                # Factor 1: RSI (30 points)
                rsi = latest.get('rsi_14', 50)
                if rsi < 30:  # Oversold
                    score += 30
                    reasons.append(f"Oversold RSI ({rsi:.1f})")
                elif rsi > 70:  # Overbought
                    score -= 30
                    reasons.append(f"Overbought RSI ({rsi:.1f})")

                # Factor 2: MACD momentum (25 points)
                macd_hist = latest.get('macd_histogram', 0)
                if macd_hist > 0:
                    score += 25
                    reasons.append("Positive MACD momentum")
                else:
                    score -= 25

                # Factor 3: Position vs MAs (20 points)
                if latest.get('above_sma_20', False) and latest.get('above_sma_50', False):
                    score += 20
                    reasons.append("Above key MAs")
                elif not latest.get('above_sma_20', False):
                    score -= 20

                # Factor 4: Volume spike (15 points)
                if latest.get('volume_spike', False):
                    score += 15
                    reasons.append("Volume spike detected")

                # Factor 5: Volatility (10 points)
                volatility = latest.get('volatility', 0)
                if 0.15 < volatility < 0.40:  # Sweet spot for intraday
                    score += 10
                    reasons.append(f"Optimal volatility ({volatility:.2f})")

                scores.append({
                    'symbol': symbol,
                    'score': score,
                    'latest_price': latest.get('latest_price', 0),
                    'rsi_14': rsi,
                    'macd_histogram': macd_hist,
                    'volatility': volatility,
                    'volume_spike': latest.get('volume_spike', False),
                    'reasons': ' | '.join(reasons) if reasons else 'Neutral'
                })

            except Exception as e:
                logger.error(f"Error scoring {symbol}: {e}")
                continue

        # Convert to DataFrame and sort
        df_scores = pd.DataFrame(scores)
        if not df_scores.empty:
            df_scores = df_scores.sort_values('score', ascending=False)

        return df_scores

    def predict_gainers(self, df_scores: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Get top predicted gainers"""
        gainers = df_scores[df_scores['score'] > 0].head(top_n)
        return gainers

    def predict_losers(self, df_scores: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Get top predicted losers"""
        losers = df_scores[df_scores['score'] < 0].tail(top_n)
        return losers.sort_values('score')

    # ==================== DISPLAY ====================

    def display_predictions(self, df: pd.DataFrame, title: str):
        """Display predictions in a formatted table"""
        print(f"\n{'=' * 100}")
        print(f"{title.center(100)}")
        print(f"{'=' * 100}\n")

        if df.empty:
            print("No predictions available.")
            return

        # Format for display
        display_df = df[[
            'symbol', 'score', 'latest_price', 'rsi_14', 'macd_histogram',
            'volatility', 'volume_spike', 'reasons'
        ]].copy()

        display_df['score'] = display_df['score'].apply(lambda x: f"{x:+.1f}")
        display_df['latest_price'] = display_df['latest_price'].apply(lambda x: f"${x:.2f}")
        display_df['rsi_14'] = display_df['rsi_14'].apply(lambda x: f"{x:.1f}")
        display_df['macd_histogram'] = display_df['macd_histogram'].apply(lambda x: f"{x:+.4f}")
        display_df['volatility'] = display_df['volatility'].apply(lambda x: f"{x:.2%}")
        display_df['volume_spike'] = display_df['volume_spike'].apply(lambda x: 'YES' if x else 'NO')

        display_df.columns = [
            'Symbol', 'Score', 'Price', 'RSI-14', 'MACD', 'Vol%', 'Vol Spike', 'Reasons'
        ]

        print(display_df.to_string(index=False))
        print(f"\n{'=' * 100}\n")

    # ==================== FULL PIPELINE ====================

    def run_prediction(self, universe: str = 'sp500', limit: int = None):
        """Run the full prediction pipeline"""
        print("\n" + "=" * 100)
        print("OPENING HOUR STOCK PREDICTOR".center(100))
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(100))
        print("=" * 100 + "\n")

        # Step 1: Get universe
        symbols = self.download_universe(universe)
        if limit:
            symbols = symbols[:limit]
            logger.info(f"Limited to first {limit} symbols for testing")

        # Step 2: Download data
        logger.info(f"Step 1/4: Downloading data for {len(symbols)} stocks...")
        stock_data = self.download_historical_data(symbols)

        if not stock_data:
            logger.error("No data downloaded. Exiting.")
            return

        # Step 3: Calculate indicators
        logger.info(f"Step 2/4: Calculating technical indicators...")
        analyzed_data = self.calculate_indicators(stock_data)

        # Step 4: Score stocks
        logger.info(f"Step 3/4: Scoring stocks...")
        df_scores = self.score_stocks(analyzed_data)

        # Step 5: Generate predictions
        logger.info(f"Step 4/4: Generating predictions...")
        top_n = self.config.get('prediction', {}).get('top_n_gainers', 10)

        gainers = self.predict_gainers(df_scores, top_n)
        losers = self.predict_losers(df_scores, top_n)

        # Display results
        self.display_predictions(gainers, "TOP 10 PREDICTED OPENING HOUR GAINERS")
        self.display_predictions(losers, "TOP 10 PREDICTED OPENING HOUR LOSERS")

        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        gainers_file = f'predictions_gainers_{timestamp}.csv'
        losers_file = f'predictions_losers_{timestamp}.csv'

        gainers.to_csv(gainers_file, index=False)
        losers.to_csv(losers_file, index=False)

        print(f"Predictions saved to:")
        print(f"  - {gainers_file}")
        print(f"  - {losers_file}\n")

        return gainers, losers


# ==================== COMMAND-LINE INTERFACE ====================

def display_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("OPENING HOUR STOCK PREDICTOR - MAIN MENU".center(60))
    print("=" * 60)
    print("\n1. Predict Opening Hour Gainers (Top 10)")
    print("2. Predict Opening Hour Losers (Top 10)")
    print("3. Analyze Specific Stock")
    print("4. Run Full Analysis (S&P 500)")
    print("5. Run Quick Test (10 stocks)")
    print("6. Download Latest Data")
    print("7. View Configuration")
    print("0. Exit")
    print("\n" + "=" * 60)


def main():
    """Main entry point"""
    predictor = OpeningHourPredictor()

    while True:
        display_menu()
        choice = input("\nSelect option (0-7): ").strip()

        if choice == '0':
            print("\nExiting... Goodbye!")
            break

        elif choice == '1' or choice == '2':
            print(f"\nRunning {'gainers' if choice == '1' else 'losers'} prediction...")
            gainers, losers = predictor.run_prediction(universe='sp500', limit=50)

            if choice == '1':
                predictor.display_predictions(gainers, "TOP 10 PREDICTED GAINERS")
            else:
                predictor.display_predictions(losers, "TOP 10 PREDICTED LOSERS")

        elif choice == '3':
            symbol = input("\nEnter stock symbol (e.g., AAPL): ").strip().upper()
            print(f"\nAnalyzing {symbol}...")

            # Download data for single stock
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

            try:
                df = predictor.data_acquirer.download_stock(symbol, start_date, end_date, '5m')
                df_analyzed = predictor.quant_analyzer.calculate_all_indicators(df)
                metrics = predictor.quant_analyzer.get_latest_metrics(df_analyzed)

                print(f"\n{symbol} - Latest Metrics:")
                print("-" * 50)
                for key, value in metrics.items():
                    print(f"{key:25s}: {value}")

            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")

        elif choice == '4':
            print("\nRunning full S&P 500 analysis...")
            gainers, losers = predictor.run_prediction(universe='sp500')

        elif choice == '5':
            print("\nRunning quick test (10 stocks)...")
            gainers, losers = predictor.run_prediction(universe='sp500', limit=10)

        elif choice == '6':
            print("\nDownloading latest data...")
            symbols = get_sp500_symbols()[:10]  # Test with 10 stocks
            stock_data = predictor.download_historical_data(symbols)
            print(f"Downloaded data for {len(stock_data)} stocks")

        elif choice == '7':
            print("\nCurrent Configuration:")
            print("-" * 60)
            print(yaml.dump(predictor.config, default_flow_style=False))

        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()
