# Shared Resources

This directory contains shared code, utilities, and types used across multiple applications.

## Directory Structure

### `/shared/lib`
Shared libraries and modules:
- Common financial calculations
- Data access layers
- Authentication modules
- Logging frameworks

### `/shared/utils`
Utility functions:
- Date/time utilities
- Number formatting
- Data validation
- String manipulation

### `/shared/types`
Shared type definitions:
- TypeScript interfaces
- Data models
- API contracts
- Validation schemas

### `/shared/constants`
Application constants:
- Configuration values
- Enum definitions
- Error codes
- Magic numbers

## Usage

Import shared code in your applications:

```javascript
// Example
import { calculateROI } from '@shared/lib/financial';
import { formatCurrency } from '@shared/utils/formatting';
import { Portfolio } from '@shared/types/models';
```

## Development Guidelines

1. Keep shared code generic and reusable
2. Document all exported functions and types
3. Include unit tests for shared code
4. Version shared modules appropriately
5. Avoid circular dependencies

## Testing

All shared code should have comprehensive test coverage in `/tests/unit/shared`.
