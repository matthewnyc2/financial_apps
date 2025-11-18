# Example MCP Server: Market Data Server

This is an example MCP server that provides real-time market data.

## Server Configuration

```json
{
  "name": "market-data-server",
  "version": "1.0.0",
  "protocol": "mcp",
  "endpoints": {
    "quotes": "/api/v1/quotes",
    "historical": "/api/v1/historical",
    "stream": "/api/v1/stream"
  },
  "authentication": "api-key",
  "rate_limits": {
    "quotes": 100,
    "historical": 50,
    "stream": 10
  }
}
```

## Supported Operations

### Get Real-time Quote
```json
{
  "operation": "getQuote",
  "parameters": {
    "symbol": "AAPL"
  }
}
```

### Get Historical Data
```json
{
  "operation": "getHistorical",
  "parameters": {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "interval": "1d"
  }
}
```

### Subscribe to Real-time Stream
```json
{
  "operation": "subscribe",
  "parameters": {
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "fields": ["last", "bid", "ask", "volume"]
  }
}
```

## Implementation

See `/mcp/servers/market-data-server/` for full implementation.

## Authentication

Use API key in header:
```
Authorization: Bearer YOUR_API_KEY
```
