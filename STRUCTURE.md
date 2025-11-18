# Directory Structure Overview

This document provides a complete overview of the financial apps monorepo structure.

## 📁 Complete Directory Tree

```
financial_apps/
│
├── .github/                          # GitHub-specific configurations
│   ├── ISSUE_TEMPLATE/              # Issue templates for bug reports, features, etc.
│   └── workflows/                   # GitHub Actions CI/CD workflows
│
├── apps/                            # 🎯 REQUIREMENT 1: Financial Applications
│   └── [Your Apps Here]/           # Each app in its own directory
│       ├── src/                    # Source code
│       ├── tests/                  # App-specific tests
│       ├── docs/                   # App documentation
│       ├── config/                 # App configuration
│       └── README.md              # App-specific README
│
├── claude/                          # 🎯 REQUIREMENT 2: Claude AI Resources
│   ├── tasks/                      # Predefined tasks for Claude
│   │   ├── portfolio-analysis.example.md
│   │   └── [Your tasks here]/
│   ├── skills/                     # Reusable Claude skills
│   │   ├── financial-calculations.example.md
│   │   └── [Your skills here]/
│   └── subagents/                  # Specialized subagents
│       ├── market-analysis-agent.example.md
│       └── [Your subagents here]/
│
├── mcp/                            # 🎯 REQUIREMENT 3: MCP Resources
│   ├── servers/                    # MCP server implementations
│   │   ├── market-data-server.example.md
│   │   └── [Your servers here]/
│   ├── clients/                    # MCP client implementations
│   │   ├── trading-client.example.md
│   │   └── [Your clients here]/
│   └── configs/                    # MCP configurations
│       ├── config.example.json
│       └── [Your configs here]/
│
├── data/                           # 🎯 REQUIREMENT 4: Financial Data
│   ├── raw/                        # Raw unprocessed data
│   ├── processed/                  # Cleaned and processed data
│   ├── market/                     # Current market data
│   ├── historical/                 # Historical archives
│   └── real-time/                  # Real-time data streams
│
├── shared/                         # Shared code across applications
│   ├── lib/                        # Shared libraries
│   ├── utils/                      # Utility functions
│   ├── types/                      # Type definitions (TypeScript, etc.)
│   └── constants/                  # Application constants
│
├── config/                         # Environment-specific configurations
│   ├── development/                # Dev environment configs
│   ├── staging/                    # Staging environment configs
│   └── production/                 # Production environment configs
│
├── docs/                           # Documentation
│   ├── architecture/               # Architecture documentation
│   ├── api/                        # API documentation
│   ├── guides/                     # How-to guides
│   └── tutorials/                  # Step-by-step tutorials
│
├── tools/                          # Development and operations tools
│   ├── scripts/                    # Utility scripts
│   ├── ci/                         # CI/CD tools and configs
│   └── deployment/                 # Deployment tools (IaC, K8s, etc.)
│
├── tests/                          # Test suites
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests
│
├── .gitignore                      # Git ignore rules (protects sensitive data)
├── README.md                       # Main repository README
├── CONTRIBUTING.md                 # Contribution guidelines
└── QUICKSTART.md                   # Quick start guide
```

## 📊 Directory Statistics

- **Total Directories**: 41
- **Core Requirement Directories**: 4 (apps, claude, mcp, data)
- **Supporting Directories**: 9 categories
- **Subdirectories**: 28
- **Documentation Files**: 16 READMEs
- **Example Files**: 6 examples

## 🎯 Core Requirements Mapping

### 1. Multiple Unrelated Financial Apps (`/apps`)

```
apps/
├── portfolio-tracker/
├── trading-bot/
├── expense-manager/
├── investment-analyzer/
└── [more apps...]
```

**Purpose**: Each app is independent, self-contained, and can be developed/deployed separately.

### 2. Claude Tasks, Skills, and Subagents (`/claude`)

```
claude/
├── tasks/              # Task definitions (analysis, reporting, etc.)
├── skills/             # Reusable capabilities (calculations, workflows)
└── subagents/          # Specialized agents (risk, market analysis, etc.)
```

**Purpose**: AI-powered automation and analysis for financial operations.

### 3. MCP Related Files (`/mcp`)

```
mcp/
├── servers/            # MCP server implementations
├── clients/            # MCP client implementations
└── configs/            # Server/client configurations
```

**Purpose**: Model Context Protocol integration for financial services.

### 4. Financial Data (`/data`)

```
data/
├── raw/               # Unprocessed source data
├── processed/         # Cleaned, normalized data
├── market/            # Current market data
├── historical/        # Historical archives
└── real-time/         # Live data streams
```

**Purpose**: Organized storage for all financial data.

## 🏗️ Supporting Infrastructure

### Shared Code (`/shared`)

Reusable code across multiple applications:
- **Libraries**: Common financial calculations, data access
- **Utilities**: Formatting, validation, helpers
- **Types**: Shared type definitions and interfaces
- **Constants**: Configuration values, enums, error codes

### Configuration (`/config`)

Environment-specific settings:
- **Development**: Local development settings
- **Staging**: Pre-production testing
- **Production**: Live deployment settings

### Documentation (`/docs`)

Comprehensive project documentation:
- **Architecture**: System design, tech stack decisions
- **API**: API specifications and contracts
- **Guides**: How-to guides and best practices
- **Tutorials**: Step-by-step learning materials

### Tools (`/tools`)

Development and operations utilities:
- **Scripts**: Automation, data processing, setup scripts
- **CI**: Build, test, and deployment automation
- **Deployment**: IaC, containerization, orchestration

### Tests (`/tests`)

Quality assurance:
- **Unit**: Component-level tests
- **Integration**: System integration tests
- **E2E**: Full workflow and user acceptance tests

## 🔒 Security & Data Protection

### .gitignore Coverage

The repository is configured to protect:
- ✅ API keys and credentials
- ✅ Environment configuration files
- ✅ Large data files (CSV, JSON, Parquet)
- ✅ Database files
- ✅ Build artifacts
- ✅ Dependencies (node_modules, etc.)
- ✅ Temporary files

### .gitkeep Files

Empty directories include `.gitkeep` files to preserve structure in version control.

## 📚 Documentation Coverage

Every major directory includes:
1. **README.md** - Purpose, usage, and guidelines
2. **Example files** - Practical usage demonstrations
3. **References** - Links to related documentation

## 🚀 Usage Patterns

### Adding a New Component

1. **New App**: `mkdir apps/my-app && cd apps/my-app`
2. **Claude Task**: Create in `claude/tasks/my-task.md`
3. **MCP Server**: Create in `mcp/servers/my-server/`
4. **Data Source**: Add to appropriate `data/` subdirectory

### Importing Shared Code

```javascript
// Example imports
import { calculateROI } from '@shared/lib/financial';
import { formatCurrency } from '@shared/utils/formatting';
import { Portfolio } from '@shared/types/models';
import { API_ENDPOINTS } from '@shared/constants/api';
```

### Running Tests

```bash
npm test                  # All tests
npm run test:unit        # Unit tests
npm run test:integration # Integration tests
npm run test:e2e         # E2E tests
```

## 📖 Documentation Index

- **[Main README](../README.md)** - Repository overview
- **[Quick Start](../QUICKSTART.md)** - Getting started guide
- **[Contributing](../CONTRIBUTING.md)** - Development guidelines
- **[Apps](../apps/README.md)** - Application guidelines
- **[Claude](../claude/README.md)** - Claude AI resources
- **[MCP](../mcp/README.md)** - MCP integration
- **[Data](../data/README.md)** - Data management
- **[Shared](../shared/README.md)** - Shared code
- **[Config](../config/README.md)** - Configuration
- **[Docs](../docs/README.md)** - Documentation
- **[Tools](../tools/README.md)** - Development tools
- **[Tests](../tests/README.md)** - Testing

## 🎓 Learning Path

1. Start with [QUICKSTART.md](../QUICKSTART.md)
2. Review [CONTRIBUTING.md](../CONTRIBUTING.md)
3. Explore example files in each directory
4. Check component-specific READMEs
5. Begin building your first application!

## 💡 Best Practices

1. **Keep apps independent** - Minimal coupling between apps
2. **Use shared code** - Don't duplicate common functionality
3. **Document changes** - Update READMEs when adding features
4. **Test thoroughly** - Write tests for new code
5. **Secure by default** - Never commit secrets
6. **Organize data** - Use appropriate data/ subdirectories
7. **Version configurations** - Use environment-specific configs

## 📞 Getting Help

- Check the relevant README in each directory
- Review example files for usage patterns
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines
- Open an issue for bugs or questions

---

**Last Updated**: 2025-11-18  
**Structure Version**: 1.0.0
