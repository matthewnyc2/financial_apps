# Example Subagent: Market Analysis Agent

This subagent specializes in market analysis and trend detection.

## Responsibilities

1. **Technical Analysis**
   - Identify chart patterns
   - Calculate technical indicators
   - Detect trends and reversals

2. **Sentiment Analysis**
   - Analyze market sentiment from news
   - Social media sentiment tracking
   - Fear & Greed index monitoring

3. **Market Correlation**
   - Identify correlations between assets
   - Sector rotation analysis
   - Inter-market relationships

## Configuration

```json
{
  "name": "market-analysis-agent",
  "capabilities": [
    "technical-analysis",
    "sentiment-analysis",
    "correlation-analysis"
  ],
  "data_sources": [
    "market-data-api",
    "news-feeds",
    "social-media"
  ],
  "update_frequency": "real-time"
}
```

## Usage

Invoke this subagent for:
- Daily market analysis reports
- Trend detection alerts
- Correlation insights
- Trading signal generation
