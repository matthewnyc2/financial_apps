#!/usr/bin/env python3
"""
Comprehensive Stock Market Data Downloader

Downloads historical data for all major US stock market indices and their constituents.
Supports S&P 500, NASDAQ 100, Russell 2000, Dow Jones 30, and more.

Usage:
    python data_downloader.py --indices all --period 10y
    python data_downloader.py --indices SP500 NASDAQ100 --period 5y --interval 1d
"""

import os
import sys
import json
import argparse
import warnings
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

import pandas as pd
import numpy as np

# Try to import yfinance, provide helpful error if not available
try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance is required. Install with: pip install yfinance")
    sys.exit(1)

# Suppress yfinance warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*parse_dates.*')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockDataDownloader:
    """
    Comprehensive stock market data downloader supporting multiple indices.
    """

    # Index ticker symbols
    INDEX_TICKERS = {
        'SP500': '^GSPC',
        'NASDAQ100': '^NDX',
        'NASDAQ': '^IXIC',
        'DOWJONES': '^DJI',
        'RUSSELL2000': '^RUT',
        'VIX': '^VIX',
    }

    # Well-known constituent lists (top holdings as of 2024)
    # For complete lists, would need to scrape from official sources
    SP500_TOP_50 = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'LLY',
        'V', 'XOM', 'JPM', 'JNJ', 'WMT', 'MA', 'PG', 'AVGO', 'HD', 'CVX',
        'MRK', 'ABBV', 'COST', 'PEP', 'KO', 'ADBE', 'CRM', 'MCD', 'CSCO', 'TMO',
        'ACN', 'ABT', 'LIN', 'NFLX', 'NKE', 'AMD', 'DHR', 'DIS', 'WFC', 'VZ',
        'TXN', 'CMCSA', 'ORCL', 'PM', 'INTU', 'COP', 'NEE', 'BMY', 'UPS', 'QCOM'
    ]

    NASDAQ100_TOP_30 = [
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',
        'ADBE', 'NFLX', 'PEP', 'AMD', 'CSCO', 'INTC', 'CMCSA', 'TXN', 'QCOM', 'INTU',
        'AMGN', 'AMAT', 'HON', 'SBUX', 'ISRG', 'ADP', 'BKNG', 'GILD', 'ADI', 'VRTX'
    ]

    DOWJONES_30 = [
        'AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'MCD', 'CAT', 'V', 'AMGN', 'BA',
        'HON', 'IBM', 'CRM', 'TRV', 'JPM', 'AXP', 'JNJ', 'PG', 'CVX', 'WMT',
        'MRK', 'DIS', 'NKE', 'MMM', 'KO', 'DOW', 'CSCO', 'VZ', 'INTC', 'WBA'
    ]

    RUSSELL2000_SAMPLE = [
        'AMC', 'GME', 'BBBY', 'PLTR', 'SOFI', 'RIVN', 'LCID', 'F', 'AAL', 'PLUG'
    ]

    def __init__(self, data_dir: str = None):
        """
        Initialize the downloader.

        Args:
            data_dir: Directory to save downloaded data (default: ../data/)
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.indices_dir = self.data_dir / 'indices'
        self.stocks_dir = self.data_dir / 'stocks'
        self.metadata_dir = self.data_dir / 'metadata'

        for dir_path in [self.indices_dir, self.stocks_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Data directory: {self.data_dir}")

    def download_ticker(
        self,
        ticker: str,
        period: str = '10y',
        interval: str = '1d',
        save_dir: Path = None
    ) -> Optional[pd.DataFrame]:
        """
        Download historical data for a single ticker.

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            save_dir: Directory to save CSV file

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            logger.info(f"Downloading {ticker} ({period}, {interval})...")

            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No data returned for {ticker}")
                return None

            # Add ticker column
            df['Ticker'] = ticker

            # Save to CSV if directory provided
            if save_dir:
                save_dir.mkdir(parents=True, exist_ok=True)
                csv_path = save_dir / f"{ticker}_{period}_{interval}.csv"
                df.to_csv(csv_path)
                logger.info(f"Saved {ticker} to {csv_path} ({len(df)} rows)")

            return df

        except Exception as e:
            logger.error(f"Error downloading {ticker}: {e}")
            return None

    def download_index(
        self,
        index_name: str,
        period: str = '10y',
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """
        Download index data (e.g., S&P 500 index itself).

        Args:
            index_name: Name of index (SP500, NASDAQ100, etc.)
            period: Time period
            interval: Data interval

        Returns:
            DataFrame with index data
        """
        if index_name not in self.INDEX_TICKERS:
            logger.error(f"Unknown index: {index_name}")
            logger.info(f"Available indices: {list(self.INDEX_TICKERS.keys())}")
            return None

        ticker = self.INDEX_TICKERS[index_name]
        return self.download_ticker(ticker, period, interval, self.indices_dir)

    def download_constituents(
        self,
        index_name: str,
        period: str = '10y',
        interval: str = '1d',
        max_stocks: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Download all constituent stocks for an index.

        Args:
            index_name: Name of index
            period: Time period
            interval: Data interval
            max_stocks: Maximum number of stocks to download (None for all)

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        # Get constituent list
        if index_name == 'SP500':
            constituents = self.get_sp500_constituents()
        elif index_name == 'NASDAQ100':
            constituents = self.NASDAQ100_TOP_30
        elif index_name == 'DOWJONES':
            constituents = self.DOWJONES_30
        elif index_name == 'RUSSELL2000':
            constituents = self.RUSSELL2000_SAMPLE
        else:
            logger.error(f"No constituent list for {index_name}")
            return {}

        if max_stocks:
            constituents = constituents[:max_stocks]

        logger.info(f"Downloading {len(constituents)} constituents for {index_name}...")

        # Create index-specific directory
        index_dir = self.stocks_dir / index_name.lower()

        results = {}
        for i, ticker in enumerate(constituents, 1):
            logger.info(f"[{i}/{len(constituents)}] Processing {ticker}...")
            df = self.download_ticker(ticker, period, interval, index_dir)
            if df is not None:
                results[ticker] = df

        logger.info(f"Successfully downloaded {len(results)}/{len(constituents)} stocks")
        return results

    def get_sp500_constituents(self) -> List[str]:
        """
        Get S&P 500 constituent tickers.

        Returns:
            List of ticker symbols
        """
        try:
            # Try to get from Wikipedia
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()

            # Clean tickers (replace dots with hyphens for Yahoo Finance)
            tickers = [t.replace('.', '-') for t in tickers]

            logger.info(f"Retrieved {len(tickers)} S&P 500 constituents from Wikipedia")
            return tickers

        except Exception as e:
            logger.warning(f"Could not fetch S&P 500 constituents from Wikipedia: {e}")
            logger.info("Using predefined top 50 S&P 500 stocks")
            return self.SP500_TOP_50

    def download_all_indices(
        self,
        period: str = '10y',
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Download all major market indices.

        Args:
            period: Time period
            interval: Data interval

        Returns:
            Dictionary mapping index name to DataFrame
        """
        results = {}
        for index_name in self.INDEX_TICKERS.keys():
            df = self.download_index(index_name, period, interval)
            if df is not None:
                results[index_name] = df

        return results

    def create_combined_dataset(
        self,
        index_name: str,
        period: str = '10y'
    ) -> pd.DataFrame:
        """
        Create a combined dataset with all stocks for an index.

        Args:
            index_name: Name of index
            period: Time period

        Returns:
            Combined DataFrame with all stocks
        """
        index_dir = self.stocks_dir / index_name.lower()

        if not index_dir.exists():
            logger.error(f"No data found for {index_name}")
            return pd.DataFrame()

        # Load all CSV files
        csv_files = list(index_dir.glob(f"*_{period}_*.csv"))

        if not csv_files:
            logger.error(f"No CSV files found in {index_dir}")
            return pd.DataFrame()

        logger.info(f"Combining {len(csv_files)} files for {index_name}...")

        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error reading {csv_file}: {e}")

        combined = pd.concat(dfs, ignore_index=False)

        # Save combined dataset
        output_path = self.data_dir / f"{index_name.lower()}_combined_{period}.csv"
        combined.to_csv(output_path)
        logger.info(f"Saved combined dataset to {output_path} ({len(combined)} rows)")

        return combined

    def generate_metadata(self) -> Dict:
        """
        Generate metadata about downloaded data.

        Returns:
            Dictionary with metadata
        """
        metadata = {
            'download_date': datetime.now().isoformat(),
            'data_directory': str(self.data_dir),
            'indices': {},
            'stocks': {}
        }

        # Scan indices
        for csv_file in self.indices_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                metadata['indices'][csv_file.stem] = {
                    'rows': len(df),
                    'start_date': str(df.index.min()),
                    'end_date': str(df.index.max()),
                    'file': str(csv_file)
                }
            except Exception as e:
                logger.error(f"Error reading {csv_file}: {e}")

        # Scan stock directories
        for index_dir in self.stocks_dir.iterdir():
            if index_dir.is_dir():
                csv_files = list(index_dir.glob("*.csv"))
                metadata['stocks'][index_dir.name] = {
                    'count': len(csv_files),
                    'directory': str(index_dir)
                }

        # Save metadata
        metadata_path = self.metadata_dir / 'download_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved metadata to {metadata_path}")
        return metadata

    def print_summary(self):
        """Print summary of downloaded data."""
        print("\n" + "="*80)
        print("DATA DOWNLOAD SUMMARY")
        print("="*80)

        metadata = self.generate_metadata()

        print(f"\nDownload Date: {metadata['download_date']}")
        print(f"Data Directory: {metadata['data_directory']}")

        print(f"\nIndices Downloaded: {len(metadata['indices'])}")
        for name, info in metadata['indices'].items():
            print(f"  - {name}: {info['rows']} rows ({info['start_date']} to {info['end_date']})")

        print(f"\nStock Collections:")
        for index_name, info in metadata['stocks'].items():
            print(f"  - {index_name.upper()}: {info['count']} stocks")

        print("\n" + "="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download historical stock market data'
    )

    parser.add_argument(
        '--indices',
        nargs='+',
        default=['all'],
        help='Indices to download (SP500, NASDAQ100, DOWJONES, RUSSELL2000, or all)'
    )

    parser.add_argument(
        '--period',
        default='10y',
        help='Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)'
    )

    parser.add_argument(
        '--interval',
        default='1d',
        help='Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)'
    )

    parser.add_argument(
        '--max-stocks',
        type=int,
        default=None,
        help='Maximum number of stocks per index (None for all)'
    )

    parser.add_argument(
        '--constituents',
        action='store_true',
        help='Download constituent stocks (not just index)'
    )

    parser.add_argument(
        '--data-dir',
        default=None,
        help='Directory to save data (default: ../data/)'
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = StockDataDownloader(data_dir=args.data_dir)

    # Determine which indices to download
    if 'all' in args.indices:
        indices = ['SP500', 'NASDAQ100', 'DOWJONES', 'RUSSELL2000', 'VIX']
    else:
        indices = [idx.upper() for idx in args.indices]

    logger.info(f"Starting download for indices: {indices}")
    logger.info(f"Period: {args.period}, Interval: {args.interval}")

    # Download index data
    for index_name in indices:
        downloader.download_index(index_name, args.period, args.interval)

    # Download constituents if requested
    if args.constituents:
        for index_name in indices:
            if index_name != 'VIX':  # VIX has no constituents
                downloader.download_constituents(
                    index_name,
                    args.period,
                    args.interval,
                    args.max_stocks
                )

    # Print summary
    downloader.print_summary()


if __name__ == '__main__':
    main()
