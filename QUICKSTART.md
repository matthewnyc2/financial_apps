# Quick Start Guide

Get started with the Financial Apps monorepo in minutes!

## 📦 What's Inside?

This monorepo is organized into four main areas:

1. **`/apps`** - Your financial applications
2. **`/claude`** - Claude AI tasks, skills, and subagents  
3. **`/mcp`** - Model Context Protocol servers and clients
4. **`/data`** - Financial data storage

Plus supporting infrastructure:
- `/shared` - Reusable code across apps
- `/config` - Environment configurations
- `/docs` - Documentation
- `/tools` - Development utilities
- `/tests` - Test suites

## 🚀 Quick Start Options

### Option 1: Create a New Financial App

```bash
# Create your app directory
mkdir -p apps/my-trading-app
cd apps/my-trading-app

# Initialize (choose your stack)
npm init -y                    # Node.js
# or
python -m venv venv           # Python
source venv/bin/activate
pip install -r requirements.txt

# Start building!
```

### Option 2: Add Claude AI Tasks

```bash
# Create a new task
cd claude/tasks
cp portfolio-analysis.example.md my-analysis-task.md

# Edit and customize for your needs
vim my-analysis-task.md
```

### Option 3: Setup MCP Server

```bash
# Create a new MCP server
mkdir -p mcp/servers/my-data-server
cd mcp/servers/my-data-server

# Initialize
npm init -y
npm install @modelcontextprotocol/sdk

# Create your server (see examples in mcp/servers/)
```

### Option 4: Add Financial Data

```bash
# Organize your data
cd data

# Raw data from sources
cp your-data.csv raw/

# Process and clean
python ../tools/scripts/process-data.py raw/your-data.csv processed/

# Historical archives
mv old-data.csv historical/
```

## 📚 Common Workflows

### Adding Shared Utilities

When you need code used across multiple apps:

```bash
# Create shared utility
vim shared/utils/financial-calculations.js

# Use in your app
import { calculateROI } from '@shared/utils/financial-calculations';
```

### Environment Configuration

```bash
# Copy example configs
cp config/development/.env.example config/development/.env

# Edit with your settings
vim config/development/.env

# Load in your app
NODE_ENV=development node app.js
```

### Running Tests

```bash
# Install test dependencies first
npm install

# Run all tests
npm test

# Run specific suite
npm run test:unit
npm run test:integration
```

## 🔧 Development Tools

### Available Scripts

Located in `/tools/scripts`:

```bash
# Data processing
./tools/scripts/process-data.sh

# Environment setup
./tools/scripts/setup-dev.sh

# Backup data
./tools/scripts/backup-data.sh
```

### CI/CD

GitHub Actions workflows in `.github/workflows/`:

- Automated testing on PR
- Linting and code quality checks
- Deployment automation

## 📖 Next Steps

1. **Read the main README**: `README.md`
2. **Check component READMEs**: Each directory has detailed docs
3. **Review examples**: See `.example` files throughout the repo
4. **Read contributing guide**: `CONTRIBUTING.md`

## 🎯 Common Tasks

### Task: Add a New Trading Application

```bash
# 1. Create app structure
mkdir -p apps/crypto-trader/{src,tests,docs}

# 2. Initialize
cd apps/crypto-trader
npm init -y

# 3. Add dependencies
npm install express axios

# 4. Create entry point
echo "console.log('Trading app starting...');" > src/index.js

# 5. Add README
echo "# Crypto Trader\n\nA cryptocurrency trading application." > README.md
```

### Task: Create Claude Subagent

```bash
# 1. Create subagent directory
mkdir -p claude/subagents/risk-analyzer

# 2. Copy example
cp claude/subagents/market-analysis-agent.example.md \
   claude/subagents/risk-analyzer/README.md

# 3. Customize for risk analysis
vim claude/subagents/risk-analyzer/README.md
```

### Task: Add Market Data Source

```bash
# 1. Create data directory
mkdir -p data/sources/alpha-vantage

# 2. Add fetching script
cat > tools/scripts/fetch-alpha-vantage.sh << 'EOF'
#!/bin/bash
# Fetch data from Alpha Vantage
API_KEY=${ALPHA_VANTAGE_KEY}
SYMBOL=$1
curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${SYMBOL}&apikey=${API_KEY}" \
  > data/raw/${SYMBOL}-$(date +%Y%m%d).json
EOF

chmod +x tools/scripts/fetch-alpha-vantage.sh

# 3. Fetch data
./tools/scripts/fetch-alpha-vantage.sh AAPL
```

## ⚠️ Important Notes

### Security
- **Never commit** API keys or secrets
- Use `.env` files (they're gitignored)
- Store credentials in environment variables

### Data Files
- Large data files are gitignored
- Use `.gitkeep` to preserve directory structure
- Consider Git LFS for versioned data

### Testing
- Write tests for new features
- Run tests before committing
- Maintain >80% coverage

## 🆘 Need Help?

- Check `/docs` for detailed documentation
- Review examples throughout the repo
- Open an issue for bugs or questions
- Read `CONTRIBUTING.md` for guidelines

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/matthewnyc2/financial_apps/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthewnyc2/financial_apps/discussions)
- **Documentation**: `/docs` directory

---

Happy coding! 🚀📈
