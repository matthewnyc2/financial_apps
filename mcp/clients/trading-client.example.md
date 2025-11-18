# Example MCP Client: Trading Client

This is an example MCP client for executing trades.

## Client Configuration

```json
{
  "name": "trading-client",
  "version": "1.0.0",
  "server_url": "https://api.trading-platform.com",
  "protocol": "mcp",
  "timeout": 5000,
  "retry_policy": {
    "max_retries": 3,
    "backoff": "exponential"
  }
}
```

## Usage Example

```javascript
const TradingClient = require('./trading-client');

const client = new TradingClient({
  apiKey: process.env.TRADING_API_KEY,
  serverUrl: 'https://api.trading-platform.com'
});

// Place a market order
const order = await client.placeOrder({
  symbol: 'AAPL',
  side: 'buy',
  quantity: 100,
  type: 'market'
});

// Get order status
const status = await client.getOrderStatus(order.id);

// Cancel an order
await client.cancelOrder(order.id);
```

## Supported Operations

- `placeOrder()` - Submit a new order
- `getOrderStatus()` - Check order status
- `cancelOrder()` - Cancel pending order
- `getPositions()` - Get current positions
- `getAccountInfo()` - Get account information

## Error Handling

The client includes comprehensive error handling:
- Network errors
- API rate limiting
- Invalid orders
- Insufficient funds
