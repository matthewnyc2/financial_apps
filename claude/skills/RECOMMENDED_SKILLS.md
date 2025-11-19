# Recommended Claude AI Skills for Financial Trading & Quantitative Analysis

**Last Updated:** November 19, 2025
**Total Skills:** 12
**Focus Areas:** Financial Calculations, Risk Assessment, Market Sentiment, Data Processing, Strategy Evaluation, Portfolio Rebalancing, Technical Indicators, Compliance

---

## 1. Discounted Cash Flow (DCF) Modeling

**Use Case:** Generate comprehensive valuation models for stocks and securities by projecting future free cash flows, calculating WACC, and applying discount rates. Essential for fundamental analysis and investment decision-making.

**Example Implementation:**
```python
# Claude generates complete DCF model with free cash flow projections
dcf_model = claude.create_dcf_model(
    company_ticker="AAPL",
    fcf_years=10,
    wacc_auto_calculate=True,
    include_sensitivity_table=True
)
# Output: Valuation range with scenario toggles and sensitivity analysis
```

---

## 2. Monte Carlo Risk Simulation

**Use Case:** Run probabilistic risk modeling for portfolio volatility, Value at Risk (VaR), and Conditional Value at Risk (CVaR) calculations. Enable data-driven risk assessment with statistical confidence intervals.

**Example Implementation:**
```python
# Claude performs Monte Carlo simulation for portfolio risk
risk_analysis = claude.monte_carlo_analysis(
    portfolio_assets=["AAPL", "MSFT", "GOOGL"],
    simulations=10000,
    time_horizon_days=252,
    confidence_level=0.95
)
# Returns: CVaR, VaR, drawdown probabilities
```

---

## 3. Technical Indicator Analysis

**Use Case:** Compute and interpret technical indicators (RSI, MACD, Bollinger Bands, Moving Averages) to identify trend reversals, support/resistance levels, and momentum shifts. Automates trading signal generation.

**Example Implementation:**
```python
# Claude calculates technical indicators with signal interpretation
indicators = claude.technical_analysis(
    symbol="TSLA",
    price_data=historical_prices,
    indicators=["RSI", "MACD", "SMA_20", "SMA_50", "Bollinger_Bands"],
    generate_signals=True
)
# Output: Buy/sell signals with momentum context
```

---

## 4. Market Sentiment Analysis

**Use Case:** Process financial news, earnings calls, social media, and market data to extract sentiment scores (positive/negative/neutral). Detect subtle tone shifts indicating market opportunities or risks.

**Example Implementation:**
```python
# Claude analyzes sentiment from multiple news sources
sentiment = claude.market_sentiment(
    sources=["news_feed", "earnings_transcripts", "twitter_finance"],
    asset_class="equities",
    aggregate=True,
    output_signals=True
)
# Returns: Sentiment score, confidence, trending topics, risk factors
```

---

## 5. Portfolio Risk Assessment

**Use Case:** Evaluate overall portfolio volatility, correlation matrices, concentration risk, and diversification metrics. Quantify tail risks and stress-test scenarios for regulatory and risk reporting.

**Example Implementation:**
```python
# Claude performs comprehensive portfolio risk analysis
portfolio_risk = claude.portfolio_risk_assessment(
    holdings=portfolio_dict,
    market_data=real_time_prices,
    include_correlations=True,
    stress_test_scenarios=["market_crash_2008", "pandemic_2020"],
    regulatory_framework="Basel_III"
)
# Output: VaR, CVaR, Sharpe ratio, concentration risk, compliance metrics
```

---

## 6. Comparable Company Analysis (Comps)

**Use Case:** Identify peer companies and calculate valuation multiples (EV/EBITDA, P/E, Price/Sales). Establish market-based valuation ranges for M&A, IPO, or investment analysis.

**Example Implementation:**
```python
# Claude performs peer analysis and multiples calculation
comps_analysis = claude.comparable_company_analysis(
    target_company="target_ticker",
    industry_sector="Technology",
    multiples=["EV_EBITDA", "P_E", "Price_Sales"],
    include_operating_metrics=True,
    output_valuation_range=True
)
# Returns: Peer group, multiples summary, valuation range
```

---

## 7. OFAC & KYC Compliance Checking

**Use Case:** Automatically scan customer data against OFAC sanctions lists and PEP (Politically Exposed Persons) databases. Enforce Know-Your-Customer (KYC) requirements and flag suspicious transactions for AML.

**Example Implementation:**
```python
# Claude validates customer compliance requirements
compliance_check = claude.ofac_kyc_validation(
    customer_data=customer_dict,
    transaction=transaction_details,
    check_lists=["OFAC_SDN", "EU_Sanctions", "PEP_Database"],
    threshold_amount_usd=10000,
    generate_report=True
)
# Returns: Risk level, flags, regulatory recommendations
```

---

## 8. Due Diligence Data Pack Generation

**Use Case:** Compile structured investment research including financial statements, growth trends, competitive positioning, and risk factors. Accelerate M&A, private equity, and venture due diligence workflows.

**Example Implementation:**
```python
# Claude generates comprehensive due diligence package
dd_package = claude.due_diligence_pack(
    company_ticker="PYPL",
    analysis_depth="institutional",
    include_sections=["financials", "market", "competitive", "legal", "risks"],
    export_format="markdown_with_tables"
)
# Output: Multi-section analysis document with audit trail
```

---

## 9. Real-Time Market Data Processing & Aggregation

**Use Case:** Integrate with data feeds (LSEG, Bloomberg, market APIs) to fetch, normalize, and process streaming quotes, news, and order book data. Enable real-time decision support without manual data entry.

**Example Implementation:**
```python
# Claude processes real-time market data from multiple sources
market_data = claude.aggregate_market_data(
    symbols=["AAPL", "MSFT", "NVDA"],
    data_types=["quotes", "news", "technicals", "order_book"],
    sources=["LSEG", "Financial_Modeling_Prep"],
    update_frequency="real_time",
    normalization=True
)
# Returns: Unified data model with time-series and alerts
```

---

## 10. Earnings Analysis & Growth Projection

**Use Case:** Extract and analyze earnings transcripts, guidance, and historical trends. Project forward earnings, identify beat/miss patterns, and assess management quality through natural language processing.

**Example Implementation:**
```python
# Claude analyzes earnings calls and projects growth
earnings_analysis = claude.earnings_analysis(
    company="MSFT",
    transcript_source="seekingalpha",
    analysis_type=["guidance_analysis", "beat_miss_history", "sentiment"],
    project_forward_eps=True,
    years_to_project=3
)
# Output: Earnings projections, guidance credibility, management sentiment
```

---

## 11. Portfolio Rebalancing Strategy Optimization

**Use Case:** Analyze current allocations versus target weights, calculate optimal trades, and evaluate rebalancing costs (taxes, commissions). Generate rebalancing instructions aligned with portfolio goals and constraints.

**Example Implementation:**
```python
# Claude optimizes portfolio rebalancing
rebalancing = claude.portfolio_rebalancing(
    current_holdings=portfolio_dict,
    target_allocation=target_weights,
    constraints={"tax_loss_harvesting": True, "max_rebalance_cost": 1000},
    market_outlook=market_view,
    execution_mode="phased"
)
# Output: Trade list, expected costs, impact on performance
```

---

## 12. Transaction Monitoring & Anomaly Detection

**Use Case:** Monitor transaction patterns for suspicious activity (structuring, layering, placement). Detect deviations from customer baseline behavior that indicate compliance risks or market manipulation.

**Example Implementation:**
```python
# Claude monitors transactions for anomalies
transaction_monitor = claude.transaction_anomaly_detection(
    customer_account=account_id,
    transaction_history=past_transactions,
    alert_threshold="suspicious",
    check_for=["structuring", "unusual_patterns", "regulatory_thresholds"],
    generate_aml_alert=True
)
# Returns: Risk score, flagged transactions, recommended actions
```

---

## Integration & Deployment Notes

### Key Capabilities
- **Audit Trail:** Extended thinking mode generates step-by-step reasoning for regulatory review
- **Data Security:** Enterprise plans ensure data is not used for model training
- **Real-Time Integration:** Connect to multiple financial data providers via MCP servers
- **Custom Workflows:** API-based agents for underwriting, compliance, and analysis

### Performance Benchmarks
- **Finance Agent Benchmark:** 55.3% accuracy (Sonnet 4.5)
- **Excel Financial Modeling:** 83% accuracy on complex tasks
- **Sentiment Analysis:** 75% accuracy across emotional detection and irony
- **Institutional Use:** 20% productivity gains (NBIM case study, ~213,000 hours)

### Recommended Tech Stack
```
Claude API → FastAPI Gateway → Market Data MCP
                ↓
        Financial Data Processors
        (News, Technicals, Sentiment)
                ↓
        Database Layer (Databricks, Snowflake)
                ↓
        Compliance & Risk Reporting
```

---

## Compliance & Disclaimers

These Claude AI skills are designed for **educational and institutional research purposes** with **human-in-the-loop validation**.

**Important Limitations:**
- Claude requires human review before executing trades
- Not designed for autonomous financial decision-making
- Regulatory use must include comprehensive audit trails
- All financial recommendations require compliance review
- Data retention policies must comply with local regulations

**Recommended Governance:**
- Implement robust internal AI governance frameworks
- Require human approval for material trades/decisions
- Maintain complete audit logs for regulatory examination
- Conduct regular model validation and backtesting
- Document all AI-assisted decisions and rationale

---

*Last verified: November 2025*
*Source: Anthropic Financial Services Documentation, industry research, and implementation case studies*
