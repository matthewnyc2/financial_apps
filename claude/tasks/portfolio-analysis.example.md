# Example Claude Task: Portfolio Analysis

This is an example task file for Claude to perform portfolio analysis.

## Task Description

Analyze a portfolio and provide insights on:
- Asset allocation
- Risk assessment
- Performance metrics
- Rebalancing recommendations

## Input Format

```json
{
  "portfolio": {
    "holdings": [
      {
        "symbol": "AAPL",
        "quantity": 100,
        "purchase_price": 150.00,
        "current_price": 175.00
      }
    ],
    "cash": 10000.00
  }
}
```

## Expected Output

- Summary of current allocation
- Risk metrics (volatility, beta, Sharpe ratio)
- Performance analysis
- Recommendations for optimization

## Usage

Invoke this task with portfolio data to receive comprehensive analysis.
