# Sentiment Analysis for Trading

## Overview

This document describes sentiment analysis approaches for algorithmic trading, including news sentiment scoring, social media sentiment analysis, FinBERT integration, sentiment-based signals, and aggregate sentiment indices.

## Table of Contents

1. [Introduction](#introduction)
2. [Sentiment Analysis Methods](#sentiment-analysis-methods)
3. [News Sentiment Scoring](#news-sentiment-scoring)
4. [Social Media Sentiment](#social-media-sentiment)
5. [FinBERT Integration](#finbert-integration)
6. [Sentiment-Based Signals](#sentiment-based-signals)
7. [Aggregate Sentiment Indices](#aggregate-sentiment-indices)
8. [Implementation Guide](#implementation-guide)
9. [Best Practices](#best-practices)

---

## Introduction

Sentiment analysis extracts emotional tone and opinions from text data to generate trading signals. Multiple data sources provide complementary signals:

- **News Sentiment**: Market-moving news from financial media
- **Social Media**: Retail sentiment from Twitter, Reddit, StockTwits
- **Linguistic Analysis**: Deep learning models trained on financial text

### Key Concepts

- **Compound Score**: Combined sentiment metric (-1 to +1)
- **Weighted Sentiment**: Sentiment adjusted by engagement/credibility
- **Sentiment Momentum**: Change in sentiment over time
- **Aggregate Index**: Multi-source combined sentiment indicator

---

## Sentiment Analysis Methods

### 1. VADER (Valence Aware Dictionary and sEntiment Reasoner)

#### Advantages
- Rule-based, lexicon-driven sentiment analysis
- Fast computation, no model training
- Handles social media text and emoticons well
- Interpretable scores

#### Components

```
Positive Score: Proportion of tokens classified as positive
Negative Score: Proportion of tokens classified as negative
Neutral Score: Proportion of neutral tokens
Compound Score: Normalized sentiment metric (-1 to +1)
```

#### Interpretation

- **Compound > 0.05**: Positive
- **Compound -0.05 to 0.05**: Neutral
- **Compound < -0.05**: Negative

#### Usage

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
scores = analyzer.polarity_scores("Great earnings report!")
# Output: {'neg': 0.0, 'neu': 0.5, 'pos': 0.5, 'compound': 0.6369}
```

### 2. FinBERT (Financial BERT)

#### Advantages
- Transformer-based deep learning model
- Pre-trained on financial text (10-K, 10-Q documents)
- Captures context and semantic meaning
- Superior accuracy on financial content

#### Model Details

- **Base Model**: BERT (Bidirectional Encoder Representations)
- **Training Data**: SEC filings, financial articles, earnings calls
- **Task**: Sequence classification (positive/negative/neutral)
- **Output**: Confidence scores for each class

#### Sentiment Classes

1. **Positive**: Bullish statements, optimistic outlook
2. **Negative**: Bearish statements, risk mentions
3. **Neutral**: Factual statements without sentiment

#### Fine-tuning Considerations

For domain-specific applications:
- Gather labeled financial text examples
- Fine-tune on company-specific language
- Validate on out-of-sample data

---

## News Sentiment Scoring

### Scoring Process

#### Step 1: News Ingestion
- Collect headlines and article content
- Capture metadata (source, timestamp, category)
- Clean and normalize text

#### Step 2: Headline Analysis
- Headlines carry disproportionate impact
- Analyze separately from body content
- Weight headline score higher

#### Step 3: Combined Analysis
- Analyze full article (headline + body)
- VADER for initial screening
- FinBERT for deeper semantic analysis

#### Step 4: Score Aggregation

```
Combined Score = 0.6 × VADER_Compound + 0.4 × (FinBERT_Positive - FinBERT_Negative)
```

### News Aggregation

#### Lookback Window
- **Short-term**: 1-4 hours (intraday)
- **Medium-term**: 24 hours (daily)
- **Long-term**: 1-4 weeks (weekly/monthly)

#### Metrics

```python
{
    'avg_sentiment': Mean compound score,
    'sentiment_std': Volatility of sentiment,
    'positive_count': Number of positive articles,
    'negative_count': Number of negative articles,
    'positive_ratio': % of positive articles,
    'sentiment_momentum': Change in sentiment over time
}
```

### Example: Earnings Announcement

```
Headline: "Apple Reports Record Q4 Earnings, Beats Estimates"
- Headline Sentiment: +0.78 (very positive)
- Article Sentiment: +0.62 (positive)
- News Weight: High (earnings are high-impact)
- Signal: BUY (strong positive sentiment shift)
```

---

## Social Media Sentiment

### Data Sources

#### Twitter/X
- Real-time market sentiment
- Retail investor opinions
- Market reactions and discussions
- Hashtag tracking (#stocks, $TICKER)

#### Reddit
- r/wallstreetbets, r/investing communities
- Deep-dive discussions and DD posts
- Community upvote ratios as credibility
- Comment counts as engagement

#### StockTwits
- Dedicated financial social network
- Cashtags ($TICKER)
- Real-time sentiment indicators
- High signal-to-noise for stocks

### Sentiment Weighting

#### Twitter
```python
weighted_sentiment = sentiment_score × (1 + log(likes + retweets + replies))
```

#### Reddit
```python
weighted_sentiment = sentiment_score × (1 + upvote_credibility + 0.1 × log(comments))
where upvote_credibility = |upvote_ratio - 0.5| × 2
```

### Aggregation

#### Collection Window
- 1-24 hours for intraday signals
- Multiple days for trend confirmation

#### Quality Filters
- Minimum engagement threshold
- Exclude low-credibility accounts
- Filter bot activity

#### Metrics

```python
{
    'avg_sentiment': Unweighted average,
    'weighted_avg_sentiment': Engagement-weighted,
    'bullish_posts': Count of positive posts,
    'bearish_posts': Count of negative posts,
    'bullish_ratio': % bullish posts,
    'avg_engagement': Average engagement per post,
    'post_count': Total posts in window
}
```

---

## FinBERT Integration

### Model Selection

#### ProsusAI/finbert (Recommended)
- Optimized for financial sentiment
- Well-maintained model
- Good balance of speed and accuracy

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = 'ProsusAI/finbert'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

### Inference Process

#### 1. Tokenization
```python
inputs = tokenizer(text, return_tensors='pt',
                   max_length=512, truncation=True)
```

#### 2. Model Forward Pass
```python
outputs = model(**inputs)
logits = outputs.logits
probs = torch.softmax(logits, dim=-1)
```

#### 3. Output Interpretation
```python
classes = ['negative', 'neutral', 'positive']
sentiment_idx = torch.argmax(probs)
confidence = probs[sentiment_idx]
```

### GPU Acceleration
- Use CUDA for batch processing
- Batch size: 32-64 for optimal throughput
- Memory: ~2GB for FinBERT inference

### Performance Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 96-98% on financial text |
| F1-Score | 0.92-0.96 |
| Inference Time | 100-200ms per article |
| Batch Processing | 10-50 articles/second |

---

## Sentiment-Based Signals

### Signal Generation

#### Components
1. **News Sentiment Score** (50% weight)
2. **Social Media Score** (50% weight)
3. **Sentiment Momentum** (trend modifier)
4. **Price Momentum** (confirmation signal)
5. **Volume Signal** (conviction indicator)

#### Signal Strength Calculation

```python
signal_strength = 0.5 × news_score + 0.5 × social_score
                  + 0.3 × news_momentum
                  + 0.2 × price_momentum
                  + 0.1 × volume_signal
```

Normalized to [-1, 1] range.

### Trading Recommendations

#### Thresholds

| Signal Strength | Recommendation | Confidence |
|-----------------|-----------------|------------|
| > 0.20 | BUY | signal_strength |
| > 0.10 | BUY (weak) | signal_strength |
| -0.10 to 0.10 | HOLD | 1 - |signal_strength| |
| < -0.10 | SELL (weak) | |signal_strength| |
| < -0.20 | SELL | |signal_strength| |

### Risk Management

#### Confirmation Rules
1. Require sentiment + technical alignment
2. Validate with price action patterns
3. Check volume for conviction
4. Monitor sentiment momentum for reversal

#### Position Sizing
```
Position_Size = Base_Size × Confidence × Risk_Factor
```

#### Stop Losses
- Tight stops on weak signals (confidence < 0.6)
- Wider stops on strong signals (confidence > 0.8)
- Trail stops as sentiment momentum continues

---

## Aggregate Sentiment Indices

### Index Construction

#### Multi-Source Index

```
Overall Index = 0.4 × News_Index
                + 0.3 × Social_Index
                + 0.2 × Momentum_Index
                + 0.1 × Engagement_Index
```

Each index normalized to 0-100 scale:
```
Index = 50 + (component_score × 50)
```

### Index Interpretation

| Range | Interpretation | Signal |
|-------|-----------------|--------|
| 70-100 | Very Bullish | Strong Buy |
| 60-70 | Bullish | Buy |
| 45-55 | Neutral | Hold |
| 30-40 | Bearish | Sell |
| 0-30 | Very Bearish | Strong Sell |

### Index Signals

#### Trend Analysis
- **Positive Trend**: Index increasing over time
- **Negative Trend**: Index decreasing over time
- **Divergence**: Index moves opposite to price (reversal signal)

#### Extremes
- **Overbought**: Index > 70 for extended period (correction risk)
- **Oversold**: Index < 30 for extended period (bounce potential)

#### Signal Generation Rules

```python
if index > 65 and trend > 0:
    signal = 'STRONG_BUY'
elif index > 60:
    signal = 'BUY'
elif index < 35 and trend < 0:
    signal = 'STRONG_SELL'
elif index < 40:
    signal = 'SELL'
else:
    signal = 'HOLD'
```

---

## Implementation Guide

### Installation

```bash
pip install vaderSentiment transformers torch pandas numpy
```

### Basic Usage

#### VADER Analysis
```python
from quants.programs.sentiment_analysis import VADERSentimentAnalyzer

analyzer = VADERSentimentAnalyzer()
scores = analyzer.analyze_text("Stock surged on positive guidance")
print(f"Compound score: {scores['compound']}")  # 0.68
```

#### News Scoring
```python
from quants.programs.sentiment_analysis import NewsSentimentScorer

scorer = NewsSentimentScorer(use_finbert=True)
article = scorer.score_article(
    headline="Company Reports Strong Earnings",
    content="Full earnings article text...",
    source="Reuters",
    timestamp=datetime.now()
)
```

#### Social Media Analysis
```python
from quants.programs.sentiment_analysis import SocialMediaSentimentAnalyzer

analyzer = SocialMediaSentimentAnalyzer()

# Twitter sentiment
tweet_result = analyzer.analyze_tweet(
    text="$AAPL looking bullish with that 20% move!",
    engagement_metrics={'likes': 500, 'retweets': 150, 'replies': 30}
)

# Reddit sentiment
reddit_result = analyzer.analyze_reddit_post(
    title="DD: Why $TSLA is Undervalued",
    content="Detailed analysis...",
    upvote_ratio=0.92,
    num_comments=450
)
```

#### Signal Generation
```python
from quants.programs.sentiment_analysis import SentimentSignalGenerator

generator = SentimentSignalGenerator()
signal = generator.generate_signal(
    news_sentiment=news_agg,
    social_sentiment=social_agg,
    price_momentum=0.15,
    volume_signal=0.1
)
```

#### Sentiment Index
```python
from quants.programs.sentiment_analysis import AggregateSentimentIndex

index = AggregateSentimentIndex()
index_data = index.compute_sentiment_index('AAPL', lookback_hours=24)

# Get signals
signals = index.get_index_signals(lookback_periods=5)
print(f"Signal: {signals['signal']}")
```

---

## Best Practices

### Data Quality

1. **Source Diversification**
   - Combine multiple news sources
   - Track multiple social platforms
   - Reduce single-source bias

2. **Text Cleaning**
   - Remove HTML/markup
   - Handle special characters
   - Normalize URLs and mentions

3. **Timestamp Accuracy**
   - Use precise publish times
   - Account for time zones
   - Capture market hours vs. off-hours

### Model Usage

1. **FinBERT Deployment**
   - Use GPU for batch processing
   - Cache model in production
   - Implement fallback to VADER
   - Monitor inference latency

2. **Validation**
   - Backtest signals on historical data
   - Compare to price action
   - Track false positive/negative rates
   - Validate on out-of-sample periods

### Signal Management

1. **Threshold Optimization**
   - Adjust thresholds for your strategy
   - Consider asset class characteristics
   - Account for volatility regimes
   - Optimize for Sharpe ratio

2. **Risk Controls**
   - Set position size limits
   - Use stop losses on sentiment reversals
   - Diversify sentiment sources
   - Monitor concentration risk

3. **Monitoring**
   - Track signal performance
   - Monitor source reliability
   - Detect sentiment shifts
   - Log all decisions

### Computational Efficiency

1. **Batch Processing**
   - Process articles in batches with FinBERT
   - Implement caching for repeated texts
   - Queue incoming data efficiently

2. **Real-time Updates**
   - Update indices on new data
   - Implement incremental calculations
   - Use efficient data structures

3. **Storage**
   - Archive sentiment scores
   - Maintain index history
   - Store signal logs for analysis

---

## References

- VADER: https://github.com/cjhutto/vaderSentiment
- FinBERT: https://github.com/ProsusAI/finBERT
- Transformers: https://huggingface.co/transformers/
- Sentiment Trading Research: https://arxiv.org/abs/1602.06271

---

## Disclaimer

Sentiment analysis is one signal among many. Combine with technical analysis, fundamental analysis, and risk management. Past performance does not guarantee future results. Use appropriate position sizing and stop losses.
