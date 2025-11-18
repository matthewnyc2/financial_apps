# Tests

This directory contains test suites for the financial apps monorepo.

## Directory Structure

### `/tests/unit`
Unit tests for individual components:
- Function tests
- Class tests
- Module tests
- Isolated component tests

### `/tests/integration`
Integration tests for system components:
- API integration tests
- Database integration tests
- Third-party service integration tests
- Module interaction tests

### `/tests/e2e`
End-to-end tests for complete workflows:
- User workflow tests
- Full system tests
- UI automation tests
- Cross-application tests

## Testing Framework

Choose appropriate testing frameworks:
- **JavaScript/TypeScript**: Jest, Mocha, Vitest
- **Python**: pytest, unittest
- **Go**: testing package
- **E2E**: Playwright, Cypress, Selenium

## Running Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests
npm run test:integration

# Run e2e tests
npm run test:e2e
```

## Test Guidelines

1. **Write tests first** (TDD when applicable)
2. **Maintain high coverage** (aim for >80%)
3. **Keep tests independent** (no test interdependencies)
4. **Use meaningful test names** (describe what's being tested)
5. **Mock external dependencies** in unit tests

## Test Data

- Store test fixtures in `/tests/fixtures`
- Use factories for test data generation
- Keep test data minimal and focused
- Clean up test data after tests run

## Continuous Testing

Tests should run:
- On every commit (pre-commit hooks)
- On every pull request (CI/CD)
- Nightly for full test suite
- Before deployment to any environment
