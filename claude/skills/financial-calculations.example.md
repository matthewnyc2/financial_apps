# Example Claude Skill: Financial Calculations

This skill provides common financial calculation capabilities.

## Capabilities

### 1. Return on Investment (ROI)
Calculate ROI given initial investment and current value.

### 2. Compound Annual Growth Rate (CAGR)
Calculate CAGR over a period.

### 3. Net Present Value (NPV)
Calculate NPV given cash flows and discount rate.

### 4. Internal Rate of Return (IRR)
Calculate IRR for a series of cash flows.

### 5. Portfolio Metrics
- Sharpe Ratio
- Beta
- Alpha
- Volatility

## Usage Example

```javascript
// Calculate ROI
const initialInvestment = 10000;
const currentValue = 12500;
const roi = ((currentValue - initialInvestment) / initialInvestment) * 100;
// ROI = 25%
```

## Dependencies

- Financial formulas library
- Statistical functions
