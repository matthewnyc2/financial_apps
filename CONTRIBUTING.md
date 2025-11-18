# Contributing to Financial Apps Monorepo

Thank you for your interest in contributing to the Financial Apps project! This guide will help you get started.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing opinions and experiences

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/financial_apps.git
   cd financial_apps
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up your development environment**
   - Install dependencies for the component you're working on
   - Configure environment variables (copy from `.env.example`)

## Development Workflow

### 1. Choose Your Work Area

- **New Application**: Create under `/apps/your-app-name`
- **Shared Code**: Add to `/shared`
- **Claude Resources**: Add to `/claude`
- **MCP Services**: Add to `/mcp`
- **Documentation**: Update `/docs`

### 2. Make Your Changes

- Write clean, maintainable code
- Follow existing code style
- Add comments for complex logic
- Keep changes focused and atomic

### 3. Test Your Changes

```bash
# Run relevant tests
npm test                    # All tests
npm run test:unit          # Unit tests only
npm run test:integration   # Integration tests
npm run lint              # Code linting
```

### 4. Document Your Changes

- Update relevant README files
- Add inline documentation
- Update API docs if applicable
- Include examples when helpful

## Project Structure

```
financial_apps/
├── apps/          # Applications (self-contained)
├── claude/        # Claude AI resources
├── mcp/           # MCP implementations
├── data/          # Financial data
├── shared/        # Shared code
├── config/        # Configurations
├── docs/          # Documentation
├── tools/         # Dev tools
└── tests/         # Test suites
```

See individual README files in each directory for detailed guidelines.

## Coding Standards

### General Guidelines

- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **SOLID**: Follow SOLID principles
- **Security First**: Never commit secrets or sensitive data

### Language-Specific

#### JavaScript/TypeScript
- Use ESLint with project configuration
- Prefer `const` over `let`, avoid `var`
- Use async/await over callbacks
- Add TypeScript types when applicable

#### Python
- Follow PEP 8 style guide
- Use type hints
- Use `black` for code formatting
- Use `pylint` for linting

### File Naming

- **Applications**: `kebab-case` (e.g., `portfolio-tracker`)
- **Source files**: `camelCase` or `snake_case` depending on language
- **Components**: `PascalCase` for classes/components
- **Configuration**: `kebab-case.json` or `.env`

### Git Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(portfolio): add ROI calculation feature

Add new function to calculate return on investment
for portfolio holdings.

Closes #123
```

```
fix(trading): handle connection timeout errors

Add retry logic for connection timeouts to trading API.
```

## Testing

### Test Coverage

- Aim for **>80%** code coverage
- All new features must include tests
- Update tests when modifying existing code

### Test Organization

```
tests/
├── unit/              # Unit tests
│   ├── apps/
│   └── shared/
├── integration/       # Integration tests
│   ├── api/
│   └── database/
└── e2e/              # End-to-end tests
    └── workflows/
```

### Writing Tests

```javascript
// Good test example
describe('Portfolio Calculator', () => {
  it('should calculate correct ROI for positive returns', () => {
    const roi = calculateROI(10000, 12000);
    expect(roi).toBe(20);
  });

  it('should handle negative returns', () => {
    const roi = calculateROI(10000, 8000);
    expect(roi).toBe(-20);
  });
});
```

## Documentation

### README Files

Every new application or module should include:
- Purpose and overview
- Installation instructions
- Usage examples
- Configuration options
- API documentation (if applicable)
- Contributing guidelines

### Code Documentation

```javascript
/**
 * Calculate return on investment (ROI)
 * 
 * @param {number} initialInvestment - The initial investment amount
 * @param {number} currentValue - The current value
 * @returns {number} ROI as a percentage
 * 
 * @example
 * const roi = calculateROI(10000, 12000);
 * // Returns: 20
 */
function calculateROI(initialInvestment, currentValue) {
  return ((currentValue - initialInvestment) / initialInvestment) * 100;
}
```

## Pull Request Process

### Before Submitting

1. ✅ Run all tests and ensure they pass
2. ✅ Run linter and fix any issues
3. ✅ Update documentation
4. ✅ Add/update tests for your changes
5. ✅ Verify no sensitive data is committed
6. ✅ Squash commits if needed

### PR Title

Use conventional commit format:
```
feat(component): brief description
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Related Issues
Closes #(issue number)
```

### Review Process

1. At least one approval required
2. All CI checks must pass
3. No merge conflicts
4. Documentation reviewed and approved

### After Merge

- Delete your feature branch
- Update your local repository
- Close related issues

## Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email: [security contact]
2. Include detailed description
3. Wait for response before disclosure

### Security Best Practices

- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive data
- Validate all user inputs
- Keep dependencies updated
- Follow OWASP guidelines for web applications

## Getting Help

- 📖 Check [documentation](docs/)
- 💬 Open a discussion for questions
- 🐛 Create an issue for bugs
- 📧 Contact maintainers for other inquiries

## Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributor list

Thank you for contributing! 🎉
