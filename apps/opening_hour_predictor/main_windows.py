#!/usr/bin/env python3
"""
Opening Hour Stock Predictor - Windows-Optimized Main Application
Enhanced for Windows Command Prompt with better formatting and colors.
"""

import sys
import os
import logging
import yaml
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import numpy as np

# Windows-specific imports for colored output
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # Initialize colorama for Windows
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback - no colors
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ''
    class Back:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = BLACK = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data.data_acquisition import MultiSourceDataAcquirer, get_sp500_symbols, get_nasdaq100_symbols
from analysis.quantitative import QuantitativeAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/predictor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def clear_screen():
    """Clear the console screen (Windows/Linux compatible)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text, color=Fore.CYAN):
    """Print a formatted header"""
    width = 100
    print()
    print(color + "=" * width + Style.RESET_ALL)
    print(color + text.center(width) + Style.RESET_ALL)
    print(color + "=" * width + Style.RESET_ALL)
    print()


def print_box(text, color=Fore.WHITE):
    """Print text in a box"""
    width = 100
    print(color + "+" + "-" * (width - 2) + "+")
    print(color + "| " + text.ljust(width - 4) + " |")
    print(color + "+" + "-" * (width - 2) + "+" + Style.RESET_ALL)


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

        print(f"{Fore.YELLOW}Downloading data from {start_date} to {end_date}, interval={interval}{Style.RESET_ALL}")

        max_workers = self.config.get('data', {}).get('max_download_workers', 50)
        stock_data = self.data_acquirer.download_multiple_stocks(
            symbols, start_date, end_date, interval, max_workers
        )

        return stock_data

    def calculate_indicators(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Calculate technical indicators for all stocks"""
        print(f"{Fore.YELLOW}Calculating quantitative indicators...{Style.RESET_ALL}")
        analyzed_data = self.quant_analyzer.analyze_multiple_stocks(stock_data)
        return analyzed_data

    # ==================== PREDICTION ====================

    def score_stocks(self, analyzed_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Score stocks based on opening hour criteria"""
        print(f"{Fore.YELLOW}Scoring stocks for opening hour potential...{Style.RESET_ALL}")

        scores = []

        for symbol, df in analyzed_data.items():
            try:
                latest = self.quant_analyzer.get_latest_metrics(df)

                if not latest:
                    continue

                # Calculate opening hour score
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

    def display_predictions(self, df: pd.DataFrame, title: str, is_gainers: bool = True):
        """Display predictions in a formatted table with colors"""
        color = Fore.GREEN if is_gainers else Fore.RED
        print_header(title, color)

        if df.empty:
            print(f"{Fore.YELLOW}No predictions available.{Style.RESET_ALL}")
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

        # Print with row numbers
        print(color)
        print(display_df.to_string(index=True))
        print(Style.RESET_ALL)
        print()

    # ==================== FULL PIPELINE ====================

    def run_prediction(self, universe: str = 'sp500', limit: int = None):
        """Run the full prediction pipeline"""
        clear_screen()
        print_header("OPENING HOUR STOCK PREDICTOR", Fore.CYAN)
        print(f"{Fore.WHITE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print()

        # Step 1: Get universe
        symbols = self.download_universe(universe)
        if limit:
            symbols = symbols[:limit]
            print(f"{Fore.YELLOW}Limited to first {limit} symbols for testing{Style.RESET_ALL}")

        # Progress indicators
        steps = [
            (f"Downloading data for {len(symbols)} stocks", self.download_historical_data),
            ("Calculating technical indicators", None),
            ("Scoring stocks", None),
            ("Generating predictions", None)
        ]

        try:
            # Step 1
            print_box(f"Step 1/4: {steps[0][0]}...", Fore.CYAN)
            stock_data = self.download_historical_data(symbols)

            if not stock_data:
                print(f"{Fore.RED}ERROR: No data downloaded. Exiting.{Style.RESET_ALL}")
                return

            print(f"{Fore.GREEN}✓ Downloaded {len(stock_data)} stocks successfully{Style.RESET_ALL}")
            print()

            # Step 2
            print_box(f"Step 2/4: Calculating technical indicators...", Fore.CYAN)
            analyzed_data = self.calculate_indicators(stock_data)
            print(f"{Fore.GREEN}✓ Calculated indicators for {len(analyzed_data)} stocks{Style.RESET_ALL}")
            print()

            # Step 3
            print_box(f"Step 3/4: Scoring stocks...", Fore.CYAN)
            df_scores = self.score_stocks(analyzed_data)
            print(f"{Fore.GREEN}✓ Scored {len(df_scores)} stocks{Style.RESET_ALL}")
            print()

            # Step 4
            print_box(f"Step 4/4: Generating predictions...", Fore.CYAN)
            top_n = self.config.get('prediction', {}).get('top_n_gainers', 10)

            gainers = self.predict_gainers(df_scores, top_n)
            losers = self.predict_losers(df_scores, top_n)
            print(f"{Fore.GREEN}✓ Predictions generated{Style.RESET_ALL}")
            print()

            # Display results
            self.display_predictions(gainers, "TOP 10 PREDICTED OPENING HOUR GAINERS", is_gainers=True)
            self.display_predictions(losers, "TOP 10 PREDICTED OPENING HOUR LOSERS", is_gainers=False)

            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            gainers_file = f'predictions_gainers_{timestamp}.csv'
            losers_file = f'predictions_losers_{timestamp}.csv'

            gainers.to_csv(gainers_file, index=False)
            losers.to_csv(losers_file, index=False)

            print(f"{Fore.CYAN}Predictions saved to:{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}• {gainers_file}{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}• {losers_file}{Style.RESET_ALL}")
            print()

            return gainers, losers

        except Exception as e:
            print(f"{Fore.RED}ERROR: {e}{Style.RESET_ALL}")
            logger.exception("Error in prediction pipeline")
            return None, None


# ==================== WINDOWS-OPTIMIZED CLI ====================

def display_menu():
    """Display main menu with Windows-friendly formatting"""
    clear_screen()

    print()
    print(Fore.CYAN + "╔" + "═" * 78 + "╗")
    print(Fore.CYAN + "║" + "   OPENING HOUR STOCK PREDICTOR - MAIN MENU".center(78) + "║")
    print(Fore.CYAN + "╚" + "═" * 78 + "╝" + Style.RESET_ALL)
    print()

    menu_items = [
        ("1", "Predict Opening Hour Gainers (Top 10)", Fore.GREEN),
        ("2", "Predict Opening Hour Losers (Top 10)", Fore.RED),
        ("3", "Analyze Specific Stock", Fore.YELLOW),
        ("4", "Run Full Analysis (S&P 500)", Fore.CYAN),
        ("5", "Run Quick Test (10 stocks)", Fore.MAGENTA),
        ("6", "Download Latest Data", Fore.BLUE),
        ("7", "View Configuration", Fore.WHITE),
        ("0", "Exit", Fore.RED)
    ]

    for num, desc, color in menu_items:
        print(f"  {color}{num}.{Style.RESET_ALL} {desc}")

    print()
    print(Fore.CYAN + "─" * 80 + Style.RESET_ALL)
    print()


def main():
    """Main entry point with Windows optimizations"""
    # Set console title on Windows
    if os.name == 'nt':
        os.system('title Opening Hour Stock Predictor')

    try:
        predictor = OpeningHourPredictor()
    except Exception as e:
        print(f"{Fore.RED}ERROR: Failed to initialize predictor: {e}{Style.RESET_ALL}")
        input("\nPress Enter to exit...")
        return

    while True:
        display_menu()
        choice = input(f"{Fore.CYAN}Select option (0-7): {Style.RESET_ALL}").strip()

        if choice == '0':
            clear_screen()
            print()
            print(f"{Fore.CYAN}Thank you for using Opening Hour Stock Predictor!{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Exiting... Goodbye!{Style.RESET_ALL}")
            print()
            break

        elif choice == '1' or choice == '2':
            predictor.run_prediction(universe='sp500', limit=50)
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == '3':
            clear_screen()
            print_header("ANALYZE SPECIFIC STOCK", Fore.YELLOW)
            symbol = input(f"{Fore.CYAN}Enter stock symbol (e.g., AAPL): {Style.RESET_ALL}").strip().upper()

            if not symbol:
                print(f"{Fore.RED}Invalid symbol.{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                continue

            print(f"\n{Fore.YELLOW}Analyzing {symbol}...{Style.RESET_ALL}\n")

            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

            try:
                df = predictor.data_acquirer.download_stock(symbol, start_date, end_date, '5m')
                df_analyzed = predictor.quant_analyzer.calculate_all_indicators(df)
                metrics = predictor.quant_analyzer.get_latest_metrics(df_analyzed)

                print(f"{Fore.GREEN}═" * 80)
                print(f"{symbol} - Latest Metrics".center(80))
                print(f"═" * 80 + Style.RESET_ALL)
                print()

                for key, value in metrics.items():
                    print(f"{Fore.CYAN}{key:30s}{Style.RESET_ALL}: {Fore.WHITE}{value}{Style.RESET_ALL}")
                print()

            except Exception as e:
                print(f"{Fore.RED}Error analyzing {symbol}: {e}{Style.RESET_ALL}")

            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == '4':
            gainers, losers = predictor.run_prediction(universe='sp500')
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == '5':
            gainers, losers = predictor.run_prediction(universe='sp500', limit=10)
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == '6':
            clear_screen()
            print_header("DOWNLOAD LATEST DATA", Fore.BLUE)
            symbols = get_sp500_symbols()[:10]
            stock_data = predictor.download_historical_data(symbols)
            print(f"{Fore.GREEN}Downloaded data for {len(stock_data)} stocks{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == '7':
            clear_screen()
            print_header("CURRENT CONFIGURATION", Fore.WHITE)
            print(yaml.dump(predictor.config, default_flow_style=False))
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Program interrupted by user. Exiting...{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}FATAL ERROR: {e}{Style.RESET_ALL}")
        logger.exception("Fatal error in main")
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
