# Comprehensive Guide: News Sentiment Analysis & NLP for Stock Prediction

**Research Date:** November 2025
**Purpose:** Integrating qualitative news analysis with quantitative methods for stock prediction

---

## Table of Contents

1. [NLP Models for Financial News Analysis](#1-nlp-models-for-financial-news-analysis)
2. [Sentiment Scoring Methods](#2-sentiment-scoring-methods)
3. [Free News Data Sources](#3-free-news-data-sources)
4. [Event Detection and Impact Analysis](#4-event-detection-and-impact-analysis)
5. [Social Media Sentiment](#5-social-media-sentiment)
6. [Named Entity Recognition](#6-named-entity-recognition)
7. [News Aggregation and Deduplication](#7-news-aggregation-and-deduplication)
8. [Temporal Decay of News Impact](#8-temporal-decay-of-news-impact)
9. [News Importance Weighting](#9-news-importance-weighting)
10. [Integration Architecture](#10-integration-architecture)
11. [Implementation Roadmap](#11-implementation-roadmap)

---

## 1. NLP Models for Financial News Analysis

### Overview
Financial sentiment analysis requires domain-specific models that understand financial terminology, context, and sentiment nuances unique to market communications.

### Primary Models

#### **FinBERT** (Recommended)
**Description:** Pre-trained BERT model fine-tuned specifically for financial domain sentiment analysis.

**Python Libraries:**
```python
# Installation
pip install transformers torch

# Usage
from transformers import BertForSequenceClassification, BertTokenizer
model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
```

**Available Implementations:**
- **ProsusAI/finBERT**: GitHub and Hugging Face - most popular
- **yya518/FinBERT**: Alternative fine-tuned version
- Both integrate seamlessly with Hugging Face transformers library

**Implementation Complexity:** Intermediate
- Requires: transformers>=4.45.1, torch, basic understanding of transformer models
- Setup time: 30-60 minutes for beginners
- Inference speed: 339x slower than VADER but provides significantly better accuracy
- Can run on consumer-grade hardware (CPU acceptable, GPU recommended)

**Performance:**
- State-of-the-art performance on financial sentiment tasks
- Achieves superior results on sentiment analysis, ESG classification, fraud detection
- FinBERT-LSTM hybrid models show best performance for stock prediction on NASDAQ-100 stocks

**Real-time vs Historical:**
- Best suited for: Batch processing historical data
- Can handle real-time with proper infrastructure (GPU recommended)
- Typical inference: 50-200ms per text on CPU, 10-50ms on GPU

**Academic Support:**
- "Predicting Stock Prices with FinBERT-LSTM" (2024) - arXiv:2407.16150
- "Stock Price Prediction Using FinBERT-Enhanced Sentiment with SHAP Explainability" (MDPI, 2025)
- Multimodal framework studies (2018-2023) show 8-12% improvement over baseline models

---

#### **GPT-4 / LLMs**
**Description:** Large language models with superior contextual understanding for financial sentiment.

**Python Libraries:**
```python
# OpenAI API
pip install openai langchain

# Open-source alternatives
pip install transformers # For Llama 3, Mistral, Gemma
```

**Implementation Complexity:** Advanced
- Requires: API keys (OpenAI) or significant compute (local LLMs)
- Cost: $0.01-0.03 per 1K tokens for GPT-4
- Setup time: 1-2 hours for API integration

**Performance:**
- ChatGPT outperformed FinBERT by 35% in sentiment classification
- 36% higher correlation with market returns than FinBERT
- Llama 3-70B shows highest accuracy in benchmark tests

**Real-time vs Historical:**
- API-based: Excellent for real-time (latency 1-3 seconds)
- Local deployment: Requires high-end GPU (A100, H100)
- Best for: Low-volume, high-accuracy applications

**Academic Support:**
- "Innovative Sentiment Analysis Using FinBERT, GPT-4 and Logistic Regression" (MDPI, 2024)
- "Transforming Sentiment Analysis in Financial Domain with ChatGPT" (2023)

**Limitations:**
- Large model sizes (billions of parameters)
- Higher computational and financial cost
- Potential API rate limits

---

#### **RoBERTa-Finance / BERT Variants**
**Description:** Twitter-trained and finance-tuned BERT variants.

**Python Libraries:**
```python
# Pre-trained Twitter sentiment model
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
# Trained on 198 million tweets
```

**Implementation Complexity:** Intermediate
- Similar to FinBERT in setup
- Better for social media text

**Real-time vs Historical:**
- Fast inference: Similar to FinBERT
- Optimized for shorter texts (tweets, headlines)

---

### Model Selection Guide

| Use Case | Recommended Model | Reason |
|----------|------------------|---------|
| News Articles (Historical) | FinBERT | Best accuracy for financial text |
| Social Media (Real-time) | RoBERTa-Twitter | Optimized for informal text |
| High-accuracy, Low-volume | GPT-4 | Superior contextual understanding |
| Budget/Learning | VADER | Free, fast, good starting point |
| Production (High-volume) | FinBERT | Best balance of accuracy and speed |

---

## 2. Sentiment Scoring Methods

### Lexicon-Based Methods

#### **VADER (Valence Aware Dictionary and sEntiment Reasoner)**

**Python Libraries:**
```python
# Installation
pip install nltk

# Usage
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
scores = sia.polarity_scores(text)
# Returns: {'neg': 0.0, 'neu': 0.5, 'pos': 0.5, 'compound': 0.8}
```

**Implementation Complexity:** Beginner
- Setup time: 5-10 minutes
- Zero training required
- Rule-based, lexicon approach

**Features:**
- Compound score: -1 (most negative) to +1 (most positive)
- Optimized for social media (emojis, punctuation, repetition)
- 406 positive words, 499 negative words in lexicon
- Overall accuracy: 63.3% on general sentiment tasks

**Performance:**
- Speed: 339x faster than FinBERT
- Best for: High-volume, real-time processing
- Social media accuracy: Moderate (24% exact match on tweets)

**Real-time vs Historical:**
- Excellent for real-time (microseconds per text)
- Can process millions of texts per hour on single CPU
- Perfect for streaming data (Twitter, Reddit, news feeds)

**Limitations:**
- Not finance-specific (may miss domain nuances)
- Lower accuracy than transformer models (41.3% vs 63.3% on some datasets)
- Best combined with other methods

**Academic Support:**
- Widely used in stock prediction research
- "Stock Market Sentiment Analysis in Python" (various studies)
- Often used as baseline comparison

---

#### **TextBlob**

**Python Libraries:**
```python
pip install textblob

from textblob import TextBlob
blob = TextBlob(text)
sentiment = blob.sentiment.polarity  # -1 to 1
```

**Implementation Complexity:** Beginner
- Even simpler than VADER
- Pattern-based sentiment scoring

**Performance:**
- Accuracy: 41.3% (lower than VADER)
- Better for general text, not social media
- Positive accuracy: 80.69%, Negative: 91.74% on product reviews

**Ensemble Approach:**
- VADER + TextBlob average: 70% accuracy (vs 24-35% individually on tweets)
- Recommended: Use weighted average of multiple methods

---

#### **Loughran-McDonald Financial Sentiment Dictionary**

**Python Libraries:**
```python
# Available through various financial NLP packages
pip install pysentiment2

import pysentiment2 as ps
lm = ps.LM()
tokens = lm.tokenize(text)
score = lm.get_score(tokens)
```

**Implementation Complexity:** Beginner
- Finance-specific word list
- 2,355 negative words, 354 positive words
- Includes: uncertainty, litigious, constraining word lists

**Performance:**
- Specifically designed for financial documents
- Better than general sentiment tools for 10-K, earnings calls
- Used in academic research since 2011

---

### Machine Learning Methods

#### **Point-wise Mutual Information (PMI) + Neural Networks**

**Description:** Features extracted using PMI, combined with regression models.

**Implementation Complexity:** Advanced
- Requires labeled training data
- Feature engineering needed
- Models: SVM, Random Forest, Neural Networks

**Academic Support:**
- Multiple papers use PMI with ε-support vector regression
- Effective for yearly stock price change prediction

---

### Hybrid Approaches

#### **Weighted Sentiment Indices**

**Implementation:**
```python
# Combine multiple sentiment scores with weights
def weighted_sentiment(text):
    vader_score = vader.polarity_scores(text)['compound']
    textblob_score = TextBlob(text).sentiment.polarity
    finbert_score = get_finbert_score(text)

    # Weighted combination
    final_score = (0.2 * vader_score +
                   0.2 * textblob_score +
                   0.6 * finbert_score)
    return final_score
```

**Recommended Weights:**
- FinBERT: 60% (highest accuracy)
- VADER: 20% (captures social media nuances)
- TextBlob: 20% (general sentiment baseline)

---

### Sentiment Aggregation Strategies

1. **Daily Aggregation:**
   - Mean sentiment across all articles for a day
   - Weighted by article importance/source credibility

2. **Source-Weighted:**
   - WSJ, Bloomberg, Reuters: Higher weights (0.8-1.0)
   - Social media: Lower weights (0.3-0.5)

3. **Temporal Decay:**
   - Recent news: Full weight
   - Older news: Exponential decay (see Section 8)

---

## 3. Free News Data Sources

### API-Based Sources

#### **Alpha Vantage**
**URL:** https://www.alphavantage.co/

**Features:**
- Global market news with AI-powered sentiment scores
- Official NASDAQ vendor
- Covers: stocks, forex, crypto
- Python library: `pip install alpha_vantage`

**Free Tier Limits (2024-2025):**
- **Official:** 500 API calls/day, 5 requests/minute
- **Recent reports:** May be reduced to 25 calls/day (verify current limits)
- Requires free API key

**Implementation:**
```python
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
news, meta = ts.get_news_sentiment(tickers='AAPL')
```

**Complexity:** Beginner
**Real-time:** Yes (with rate limits)
**Best for:** Production apps with moderate volume

---

#### **NewsAPI.org**
**URL:** https://newsapi.org/

**Features:**
- Global news in real-time
- JSON search results
- Covers 80+ markets, 5,000+ sources

**Free Tier:**
- Developer plan available
- Limited historical access (typically 30 days)
- Rate limits apply

**Implementation:**
```python
pip install newsapi-python

from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key='YOUR_KEY')
articles = newsapi.get_everything(q='AAPL stock',
                                  language='en',
                                  sort_by='relevancy')
```

**Complexity:** Beginner
**Best for:** Current news, headline analysis

---

#### **Marketaux**
**URL:** https://www.marketaux.com/

**Features:**
- Free finance and stock market news API
- JSON format
- 80+ markets, 5,000+ sources
- Real-time news with tagged tickers and sentiment

**Free Tier:**
- Available with limitations
- Good for getting started

**Complexity:** Beginner
**Best for:** Stock-specific news with pre-tagged tickers

---

#### **yfinance (Yahoo Finance)**
**URL:** https://github.com/ranaroussi/yfinance

**Features:**
- **Completely free** - no API key required
- Unlimited requests (unofficial, no guaranteed rate limits)
- Historical and current data
- News headlines for stocks

**Free Tier:**
- Unlimited (use responsibly)
- No authentication required

**Implementation:**
```python
pip install yfinance

import yfinance as yf
ticker = yf.Ticker("AAPL")
news = ticker.news  # Returns recent news
```

**Complexity:** Beginner (easiest)
**Limitations:**
- Unofficial API (may break)
- Limited news details compared to paid APIs
- No sentiment scores included

**Best for:** Learning, prototyping, budget projects

---

#### **Polygon.io**
**URL:** https://polygon.io/

**Features:**
- Real-time market data
- News with ticker tags

**Free Tier:**
- 5 API calls/minute
- Very limited for production
- 7-day free trial

**Complexity:** Intermediate
**Best for:** Testing only (too limited for production)

---

#### **EODHD (End of Day Historical Data)**
**URL:** https://eodhd.com/

**Features:**
- Financial news API with sentiment analysis
- 50+ million historical articles
- In-house sentiment scoring

**Free Tier:**
- Limited free tier available
- Good for historical analysis

**Complexity:** Intermediate

---

### RSS Feed Sources (Free)

#### **Google News RSS**
**Features:**
- **Completely free**
- Lightweight, no API key needed
- RSS feed for any search query
- Won't get blocked for frequent access

**Implementation:**
```python
pip install feedparser

import feedparser

# Company-specific news
url = "https://news.google.com/rss/search?q=Apple+stock&hl=en-US&gl=US&ceid=US:en"
feed = feedparser.parse(url)

for entry in feed.entries:
    print(entry.title, entry.published, entry.link)
```

**Limitations:**
- Google News API was discontinued in 2011 (official)
- RSS feeds still work and are reliable
- Less structured than API responses

**Complexity:** Beginner
**Best for:** Free, high-volume news collection

---

#### **Financial News Websites RSS**
**Available RSS Feeds:**
- Reuters: https://www.reuters.com/finance
- MarketWatch: https://www.marketwatch.com/rss/
- Seeking Alpha: Category-specific RSS feeds
- Yahoo Finance: Stock-specific RSS

**Complexity:** Beginner
**Cost:** Free

---

### Web Scraping Options

#### **Financial News Scraper Libraries**

**Python Libraries:**
```python
# finnews - Financial news aggregator
pip install finnews

from finnews import Client
news_client = Client()
cnbc_news = news_client.cnbc_news()

# fin-news - Another aggregator
pip install fin-news

# Custom scraping
pip install beautifulsoup4 requests selenium
```

**Complexity:** Intermediate to Advanced
**Legal Considerations:**
- Check terms of service
- Respect robots.txt
- Consider rate limiting
- Some sites block scrapers

**Best for:** Custom data needs when APIs insufficient

---

### Recommended Data Source Combinations

**Budget/Learning:**
1. yfinance (primary)
2. Google News RSS (supplementary)
3. VADER sentiment (free processing)

**Production (Free Tier):**
1. Alpha Vantage (500/day for key news)
2. Google News RSS (high volume collection)
3. yfinance (stock data + some news)
4. FinBERT (sentiment processing)

**Production (Paid Acceptable):**
1. Alpha Vantage Premium or Financial Modeling Prep
2. NewsAPI.org Pro
3. Benzinga News API

---

## 4. Event Detection and Impact Analysis

### Overview
Event-driven stock prediction analyzes how specific financial events (earnings, mergers, regulatory changes) impact stock prices using NLP techniques.

### Event Extraction Methods

#### **OpenIE (Open Information Extraction)**

**Description:** Extracts structured events from unstructured news text.

**Python Libraries:**
```python
# Stanford OpenIE
pip install stanford-openie

# AllenNLP for OpenIE
pip install allennlp allennlp-models
```

**Process:**
1. Extract (subject, relation, object) triples from news
2. Classify event types (merger, earnings, layoff, etc.)
3. Link events to affected companies
4. Predict uptrend/downtrend probability

**Implementation Complexity:** Advanced
- Requires NLP expertise
- Training data for event classification needed

**Academic Support:**
- "On the Importance of Text Analysis for Stock Price Prediction" (Stanford NLP, LREC 2014)
- Using text boosts prediction accuracy >10% over financial features alone
- Impact most significant in short term (1-5 days)

---

#### **8-K Report Analysis**

**Description:** U.S. public companies must file 8-K reports for significant business events.

**Event Types Covered:**
- Bankruptcies
- Layoffs
- Director elections
- Credit changes
- Mergers and acquisitions
- Material agreements

**Python Libraries:**
```python
# SEC Edgar API
pip install sec-edgar-downloader

from sec_edgar_downloader import Downloader
dl = Downloader("MyCompany", "my.email@example.com")
dl.get("8-K", "AAPL", after="2024-01-01")
```

**Implementation Complexity:** Intermediate
- Structured data, easier to parse than news
- Requires understanding of SEC filing format

**Real-time vs Historical:**
- Historical: Excellent (complete records)
- Real-time: Some delay (filings not instant)

---

#### **Named Event Detection**

**Key Event Categories:**
1. **Earnings Events:**
   - Earnings beats/misses
   - Guidance changes
   - Revenue surprises

2. **Corporate Actions:**
   - Mergers & Acquisitions
   - Stock splits
   - Dividend announcements
   - Buyback programs

3. **Management Changes:**
   - CEO/CFO departures
   - Board changes

4. **Legal/Regulatory:**
   - Lawsuits
   - Regulatory approvals/denials
   - FDA approvals (pharma)

5. **Product Events:**
   - Product launches
   - Recalls
   - Major contracts won/lost

**Detection Approach:**
```python
# Using regex + NER + classification
import re
from transformers import pipeline

# Event classifier
event_classifier = pipeline("zero-shot-classification")

event_types = ["earnings", "merger", "lawsuit", "product_launch",
               "management_change", "dividend"]

result = event_classifier(news_text, candidate_labels=event_types)
```

**Complexity:** Advanced

---

### Impact Analysis Methods

#### **Time-Boxed Performance**

**Methodology:**
1. Identify event timestamp
2. Measure stock price change in windows:
   - Immediate: 0-1 hour
   - Short-term: 1-5 days
   - Medium-term: 5-20 days
   - Long-term: 20-90 days

**Academic Finding:**
- Text impact persists up to 5 days
- Maximum impact: Day 0-1
- 10%+ relative accuracy improvement

---

#### **Event-Driven Models**

**Architecture:**
```
News Text → Event Extraction → Event Classification → Sentiment Analysis
                ↓
         Event Importance Score → Impact Prediction → Price Movement
                ↓
         Historical Prices + Technical Indicators
```

**Python Implementation:**
```python
# Pseudo-code structure
def predict_event_impact(event_text, ticker, historical_data):
    # Extract event
    event_type = classify_event(event_text)

    # Get sentiment
    sentiment = finbert_sentiment(event_text)

    # Event importance
    importance = calculate_importance(event_type, sentiment, source)

    # Combine with historical patterns
    similar_events = find_similar_historical_events(event_type, ticker)
    expected_impact = model_predict(importance, similar_events, historical_data)

    return expected_impact
```

---

### State-of-the-Art Models

#### **News-Driven Equity State Representation**

**Description:** Represents noisy equity states using news embeddings.

**Academic Support:**
- "News-driven stock prediction via noisy equity state representation" (ScienceDirect, 2021)
- Handles noisy, conflicting news signals
- Neural network approach

**Complexity:** Advanced (research-level)

---

#### **LSTM + Event Features**

**Architecture:**
- LSTM for time-series (prices)
- Event embeddings from FinBERT
- Concatenated features for prediction

**Performance:**
- Results indicate using text alongside historical prices improves predictions
- State-of-the-art: CNN, RNN, BERT-based models

**Academic Support:**
- "Natural Language Processing and Multimodal Stock Price Prediction" (arXiv, 2024)
- Multiple papers showing 10-20% improvement with event data

---

### Implementation Recommendations

**Beginner:**
1. Use pre-classified events from financial APIs (Alpha Vantage, Benzinga)
2. Simple sentiment scoring (VADER)
3. Correlation analysis between events and price

**Intermediate:**
1. Custom event extraction using NER
2. FinBERT for sentiment
3. Basic impact scoring based on event type

**Advanced:**
1. Custom event detection models
2. Deep learning for impact prediction
3. Multi-modal fusion (news + price + volume)

---

## 5. Social Media Sentiment

### Twitter/X Analysis

#### **Data Collection**

**PRAW Restrictions (2024 Update):**
- **Important:** Reddit restricted Pushshift API access to moderators only
- **Solution:** Use PRAW (Python Reddit API Wrapper) directly
- **Limitation:** PRAW only fetches recent submissions (not arbitrary historical)

**Python Libraries:**
```python
# Twitter (requires API access - now paid for most use)
pip install tweepy

# Alternative: Snscrape (no API key needed)
pip install snscrape

# Usage example
import snscrape.modules.twitter as sntwitter

query = "$AAPL lang:en"
tweets = []
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
    if i > 1000:
        break
    tweets.append([tweet.date, tweet.content, tweet.user.username])
```

**Implementation Complexity:** Intermediate
- Twitter API: Requires approval, now mostly paid
- Snscrape: Free but may be unreliable (scraping-based)

**2024-2025 Challenge:**
- Twitter API now requires paid plans for most access
- Free tier extremely limited (1,500 tweets/month)
- Consider alternative platforms or focus on Reddit

---

#### **Twitter-Specific Models**

**Pre-trained Models:**
```python
pip install transformers

from transformers import pipeline

# Twitter-specific sentiment (198M tweets training)
sentiment_pipeline = pipeline("sentiment-analysis",
                              model="cardiffnlp/twitter-roberta-base-sentiment")

result = sentiment_pipeline("$AAPL to the moon! 🚀📈")
# Output: [{'label': 'POSITIVE', 'score': 0.95}]
```

**Performance:**
- Trained on 198 million tweets
- Understands emojis, slang, hashtags
- Better than general models for Twitter data

---

#### **Academic Research**

**Key Findings:**
- "Predicting Stock Movement Using Sentiment Analysis of Twitter Feed with Neural Networks" (SCIRP)
- Twitter sentiment has proven valuable for predicting market trends
- Algorithms: Naive Bayes, Decision Trees, SVM, Random Forest, MLPClassifier
- Integration with LSTM shows 20% accuracy improvement

**Research Papers:**
- "Stock Market Prediction Using Twitter Sentiment Analysis" (ResearchGate, 2021)
- "Tweet Sentiment Analysis to Predict Stock Market" (Stanford CS224N)
- Multiple studies confirm faint but real signal for stock returns

**Limitations:**
- Signal is "intermittent and far too weak to trade on independently"
- Best combined with other signals
- Crowd chatter contains noise

---

### Reddit Sentiment

#### **Data Collection (2024 Approach)**

**Python Libraries:**
```python
pip install praw

import praw

reddit = praw.Reddit(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_SECRET',
    user_agent='Stock Sentiment Analyzer'
)

# Target subreddits
subreddits = ['wallstreetbets', 'stocks', 'investing',
              'stockmarket', 'SecurityAnalysis']

for submission in reddit.subreddit('wallstreetbets').hot(limit=100):
    print(submission.title, submission.score, submission.num_comments)
```

**Implementation Complexity:** Beginner to Intermediate
- PRAW well-documented, easy to use
- Requires Reddit API credentials (free)

**2024 Research:**
- Study collected data from 5 subreddits daily for 30 days
- Combined with S&P 500 data from Yahoo Finance
- Used VADER for sentiment analysis

---

#### **Reddit-Specific Challenges**

**Data Quality:**
- High noise-to-signal ratio
- Retail investor bias
- Meme stock influence
- Pump-and-dump schemes

**Solutions:**
1. Filter by submission score/upvotes
2. Focus on quality subreddits (r/SecurityAnalysis vs r/wallstreetbets)
3. Combine with professional news sources
4. Weight Reddit sentiment lower than news

**Academic Finding:**
- "After parsing 18 million Reddit comments spanning 8 years..."
- Faint signal exists but inconsistent
- Not sufficient for standalone trading

---

### StockTwits

#### **API Access**

**Limitations:**
- Free API: 30 most recent messages per symbol (no sentiment labels)
- Sentiment API: **Partner access only** (contact developers@stocktwits.com)
- Alternative: Web scraping (check ToS first)

**Python Implementation:**
```python
import requests

# Free API (no auth required, limited data)
symbol = "AAPL"
url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
response = requests.get(url)
data = response.json()

# Extract messages
for message in data['messages']:
    print(message['body'], message['created_at'])
```

**DIY Sentiment:**
```python
# Since sentiment not available in free API
from transformers import pipeline

sentiment = pipeline("sentiment-analysis")

for message in messages:
    score = sentiment(message['body'])
    print(score)
```

**Implementation Complexity:** Intermediate
- Free API: Beginner
- Scraping for volume: Advanced
- DIY sentiment: Intermediate

**Alternative:**
- Third-party APIs (Financial Modeling Prep, StockAPI) offer StockTwits data

---

### Social Media Sentiment Tools

#### **Market Sentiment Live**

**GitHub:** marketsentiment/mslive_public

**Features:**
- Track live sentiment from Reddit and Twitter
- Identify growing stocks
- Pre-built aggregation

**Complexity:** Intermediate (deployment required)

---

### Recommended Social Media Strategy

**For Production System:**

1. **Data Sources Priority:**
   - Reddit: Primary (easier API access, free)
   - StockTwits: Secondary (limited free access)
   - Twitter: Tertiary (expensive API, consider alternatives)

2. **Sentiment Analysis:**
   - Use twitter-roberta-base-sentiment for all platforms
   - Apply VADER as fast baseline
   - Weight: News (70%) > Reddit (20%) > Twitter/StockTwits (10%)

3. **Aggregation:**
   ```python
   def aggregate_social_sentiment(ticker, date):
       reddit_score = get_reddit_sentiment(ticker, date)
       twitter_score = get_twitter_sentiment(ticker, date)  # if available
       stocktwits_score = get_stocktwits_sentiment(ticker, date)

       # Weighted average
       social_sentiment = (reddit_score * 0.5 +
                          twitter_score * 0.25 +
                          stocktwits_score * 0.25)

       return social_sentiment
   ```

4. **Filtering:**
   - Minimum upvotes/likes threshold
   - Remove duplicate content
   - Filter obvious spam/bots
   - Focus on tickers with sufficient volume

---

### Academic Support

**Key Papers:**
- "Sentiment Analysis of Twitter Data for Predicting Stock Market" (arXiv:1610.09225)
- "Paper Trading From Sentiment Analysis on Twitter and Reddit Posts" (Stanford CS224N)
- "Stock price prediction using sentiment Based LSTM: S&P500 vs Reddit posts" (NSF, 2024)

**Consensus:**
- Social media adds marginal predictive value
- Best as supplementary signal
- Requires careful noise filtering
- Most effective for momentum/short-term prediction

---

## 6. Named Entity Recognition (NER)

### Overview
NER extracts company names, stock tickers, people, and financial entities from unstructured text, enabling automated monitoring and entity-specific sentiment analysis.

### Python Libraries

#### **spaCy** (Recommended for Production)

**Features:**
- Industrial-strength NLP library
- Fast processing (C extensions)
- Pre-trained financial models available

**Installation & Usage:**
```python
pip install spacy
python -m spacy download en_core_web_sm  # General English
python -m spacy download en_core_web_trf  # Transformer-based (better)

import spacy

nlp = spacy.load("en_core_web_sm")
text = "Apple Inc. (AAPL) reported record earnings, while Microsoft (MSFT) announced layoffs."

doc = nlp(text)
for ent in doc.ents:
    if ent.label_ in ["ORG", "PERSON", "MONEY"]:
        print(ent.text, ent.label_)

# Output:
# Apple Inc. ORG
# Microsoft ORG
```

**Implementation Complexity:** Beginner to Intermediate
- Basic NER: Beginner (10-15 minutes setup)
- Custom training: Advanced
- Speed: Extremely fast (thousands of docs/second)

---

#### **Hugging Face Transformers**

**Features:**
- State-of-the-art transformer models
- Pre-trained NER models available
- Simple pipeline interface

**Installation & Usage:**
```python
pip install transformers

from transformers import pipeline

ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")

text = "Tim Cook announced Apple's $100B investment in AI."
entities = ner_pipeline(text)

for entity in entities:
    print(f"{entity['word']}: {entity['entity']}")

# Output:
# Tim: B-PER
# Cook: I-PER
# Apple: B-ORG
```

**Implementation Complexity:** Beginner
- Pipeline API: Very simple
- Fine-tuning: Advanced

**Performance:**
- Higher accuracy than rule-based
- Slower than spaCy
- Better for complex entity recognition

---

#### **NLTK**

**Features:**
- Classic NLP library
- Good for learning
- Maximum Entropy chunking

**Installation & Usage:**
```python
pip install nltk
import nltk
nltk.download('maxent_ne_chunker')
nltk.download('words')

from nltk import ne_chunk, pos_tag, word_tokenize

text = "Apple Inc. reported earnings in New York."
tokens = word_tokenize(text)
pos_tags = pos_tag(tokens)
entities = ne_chunk(pos_tags)

print(entities)
```

**Implementation Complexity:** Intermediate
- Less accurate than modern methods
- Good for educational purposes

**Performance:**
- Classical machine learning (not deep learning)
- Lower accuracy than spaCy or Transformers
- Fast but outdated

---

### Financial-Specific NER

#### **John Snow Labs - Finance NLP**

**URL:** https://nlp.johnsnowlabs.com/financial_entity_recognition

**Features:**
- Specialized for financial documents
- Extracts: Company names, stock codes, monetary terms
- Pre-trained on financial reports

**Entities Detected:**
- Corporations
- Stock tickers
- Monetary values
- Dates
- Financial events

**Complexity:** Intermediate to Advanced
- Commercial library (Spark NLP)
- Better accuracy for financial text

---

#### **Custom Financial NER Model**

**Training Approach:**
```python
# Using spaCy for custom training
import spacy
from spacy.training import Example

# Create blank model
nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add labels
ner.add_label("TICKER")
ner.add_label("COMPANY")
ner.add_label("FINANCIAL_EVENT")

# Training data format
TRAIN_DATA = [
    ("Apple (AAPL) beat earnings expectations",
     {"entities": [(0, 5, "COMPANY"), (7, 11, "TICKER")]}),
    # ... more examples
]

# Training loop
for epoch in range(30):
    for text, annotations in TRAIN_DATA:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        nlp.update([example])
```

**Complexity:** Advanced
- Requires labeled training data
- Time-consuming but most accurate for your specific use case

---

### Stock Ticker Extraction

#### **Regex-Based Approach** (Simple)

```python
import re

def extract_tickers(text):
    # Pattern: $ followed by 1-5 uppercase letters
    pattern = r'\$([A-Z]{1,5})\b'
    tickers = re.findall(pattern, text)
    return tickers

text = "$AAPL and $MSFT are trending while $TSLA falls"
print(extract_tickers(text))  # ['AAPL', 'MSFT', 'TSLA']
```

**Pros:**
- Extremely fast
- Works well on social media (Twitter, Reddit use $ notation)

**Cons:**
- Misses tickers not prefixed with $
- False positives possible

---

#### **Combined NER + Ticker Matching**

```python
import spacy
import yfinance as yf

def extract_companies_and_tickers(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    results = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            # Try to find ticker for company name
            try:
                ticker = yf.Ticker(ent.text)
                if ticker.info:
                    results.append({
                        'company': ent.text,
                        'ticker': ticker.ticker
                    })
            except:
                pass

    # Also check for explicit ticker mentions
    tickers = re.findall(r'\$([A-Z]{1,5})\b', text)
    for ticker in tickers:
        results.append({'ticker': ticker})

    return results
```

---

### Use Cases for Stock Prediction

#### **1. Multi-Stock News Filtering**

```python
def filter_news_by_ticker(news_articles, target_ticker):
    """Extract only news mentioning specific company"""
    relevant_news = []

    for article in news_articles:
        entities = extract_entities(article['text'])
        tickers = [e['ticker'] for e in entities if 'ticker' in e]

        if target_ticker in tickers:
            relevant_news.append(article)

    return relevant_news
```

**Benefit:** Focus sentiment analysis on company-specific news

---

#### **2. Co-Mention Analysis**

```python
def analyze_co_mentions(news_articles):
    """Find which companies are mentioned together"""
    from collections import Counter

    co_mentions = Counter()

    for article in news_articles:
        tickers = extract_tickers(article['text'])
        # Count all pairs
        for i, t1 in enumerate(tickers):
            for t2 in tickers[i+1:]:
                pair = tuple(sorted([t1, t2]))
                co_mentions[pair] += 1

    return co_mentions.most_common(10)

# Use case: Identify merger rumors, partnerships, competitive analysis
```

---

#### **3. Person-Company Linkage**

```python
def extract_executive_mentions(text):
    """Link executive names to companies"""
    doc = nlp(text)

    people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    # Executive mentions often indicate important news
    if people and orgs:
        return {"people": people, "companies": orgs, "importance": "high"}
    return None

# CEO mentions correlate with higher news impact
```

---

### Academic Support

**Research:**
- "Finance Named Entity Recognition" (Fast Data Science)
- "Extraction and Representation of Financial Entities from Text" (HPI)
- NER helps banks/investment firms automate monitoring of:
  - Stock tickers
  - Merger events
  - Key dates
  - Market trends

**Benefits:**
- Automated stock mention detection
- Portfolio monitoring
- Event extraction
- Relationship mapping

---

### Implementation Recommendations

**Beginner:**
- Use spaCy with pre-trained models
- Regex for ticker extraction ($AAPL pattern)
- Simple entity filtering

**Intermediate:**
- Hugging Face transformers for better accuracy
- Combine multiple NER sources
- Entity linking to stock database

**Advanced:**
- Train custom financial NER model
- Multi-lingual entity recognition
- Real-time entity tracking with relation extraction

---

## 7. News Aggregation and Deduplication

### Overview
Financial news is often republished across multiple sources, creating redundant signals. Effective aggregation and deduplication are critical for accurate sentiment analysis.

### Python Libraries for Aggregation

#### **finnews** (Recommended for Beginners)

**Features:**
- Pre-built aggregator for financial news
- Supports: CNBC, WSJ, MarketWatch, Seeking Alpha
- Simple interface

**Installation & Usage:**
```python
pip install finnews

from finnews import Client

news_client = Client()

# CNBC News
cnbc_news = news_client.cnbc_news()
cnbc_data = cnbc_news.news_feed(topic='stocks')

# Multiple sources
wsj = news_client.wsj()
market_watch = news_client.market_watch()
```

**Complexity:** Beginner
**Coverage:** Major US financial news sources

---

#### **Financial News API** (GitHub)

**Repository:** FinancialNewsAPI/financial-news-api-python

**Features:**
- 50+ million historical articles
- Real-time news streaming
- Multi-source aggregation

**Installation:**
```python
pip install finance-news-api

from finance_news_api import FinanceNewsAPI

api = FinanceNewsAPI(api_key='YOUR_KEY')
news = api.search(
    ticker='AAPL',
    from_date='2024-01-01',
    to_date='2024-12-31'
)
```

**Complexity:** Intermediate
**Cost:** Paid API (check pricing)

---

#### **Custom RSS Aggregation**

```python
import feedparser
from datetime import datetime

class NewsAggregator:
    def __init__(self):
        self.feeds = {
            'reuters': 'https://www.reuters.com/finance/rss',
            'marketwatch': 'https://www.marketwatch.com/rss/',
            'google_news': 'https://news.google.com/rss/search?q={query}'
        }

    def aggregate_news(self, query, hours=24):
        all_articles = []

        for source, feed_url in self.feeds.items():
            if '{query}' in feed_url:
                url = feed_url.format(query=query)
            else:
                url = feed_url

            feed = feedparser.parse(url)

            for entry in feed.entries:
                article = {
                    'source': source,
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.get('summary', '')
                }
                all_articles.append(article)

        return all_articles

# Usage
aggregator = NewsAggregator()
news = aggregator.aggregate_news('Apple stock', hours=24)
```

**Complexity:** Intermediate
**Cost:** Free
**Flexibility:** High

---

### Deduplication Strategies

#### **1. Exact Title Matching** (Simple)

```python
def deduplicate_exact(articles):
    """Remove articles with identical titles"""
    seen_titles = set()
    unique_articles = []

    for article in articles:
        title_lower = article['title'].lower().strip()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_articles.append(article)

    return unique_articles
```

**Pros:** Fast, simple
**Cons:** Misses near-duplicates with slightly different titles

---

#### **2. TF-IDF + Cosine Similarity** (Recommended)

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def deduplicate_tfidf(articles, threshold=0.85):
    """Remove articles with similar content using TF-IDF"""

    # Extract text (title + summary)
    texts = [f"{a['title']} {a.get('summary', '')}" for a in articles]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Calculate similarities
    similarities = cosine_similarity(tfidf_matrix)

    # Mark duplicates
    keep = np.ones(len(articles), dtype=bool)

    for i in range(len(articles)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(articles)):
            if similarities[i, j] > threshold:
                keep[j] = False  # Mark as duplicate

    # Return unique articles
    unique_articles = [articles[i] for i in range(len(articles)) if keep[i]]
    return unique_articles

# Usage
unique_news = deduplicate_tfidf(all_articles, threshold=0.85)
```

**Complexity:** Intermediate
**Performance:** Excellent for near-duplicates
**Threshold:** 0.85 = 85% similarity → likely duplicate

---

#### **3. MinHash LSH (Scalable)**

```python
from datasketch import MinHash, MinHashLSH

def deduplicate_minhash(articles, threshold=0.8):
    """Fast deduplication for large datasets using MinHash"""

    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    minhashes = {}

    for i, article in enumerate(articles):
        text = f"{article['title']} {article.get('summary', '')}"

        # Create MinHash
        m = MinHash(num_perm=128)
        for word in text.lower().split():
            m.update(word.encode('utf8'))

        minhashes[i] = m
        lsh.insert(f"article_{i}", m)

    # Find duplicates
    duplicates = set()
    for i, minhash in minhashes.items():
        similar = lsh.query(minhash)
        if len(similar) > 1:
            # Keep first, mark others as duplicates
            similar_indices = [int(s.split('_')[1]) for s in similar]
            duplicates.update(similar_indices[1:])

    # Return unique
    unique = [articles[i] for i in range(len(articles)) if i not in duplicates]
    return unique
```

**Complexity:** Advanced
**Performance:** Best for 10,000+ articles
**Speed:** Very fast (LSH indexing)

---

#### **4. URL Deduplication**

```python
from urllib.parse import urlparse

def deduplicate_urls(articles):
    """Remove articles pointing to same URL"""
    seen_urls = set()
    unique = []

    for article in articles:
        # Normalize URL
        parsed = urlparse(article['link'])
        normalized_url = f"{parsed.netloc}{parsed.path}"

        if normalized_url not in seen_urls:
            seen_urls.add(normalized_url)
            unique.append(article)

    return unique
```

**Use Case:** When same article appears in multiple RSS feeds

---

### Advanced: Semantic Deduplication

#### **Using Sentence Transformers**

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def deduplicate_semantic(articles, threshold=0.85):
    """Remove semantically similar articles"""

    texts = [f"{a['title']} {a.get('summary', '')}" for a in articles]

    # Generate embeddings
    embeddings = model.encode(texts)

    # Calculate similarities
    similarities = cosine_similarity(embeddings)

    # Mark duplicates
    keep = np.ones(len(articles), dtype=bool)

    for i in range(len(articles)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(articles)):
            if similarities[i, j] > threshold:
                keep[j] = False

    return [articles[i] for i in range(len(articles)) if keep[i]]
```

**Complexity:** Advanced
**Accuracy:** Best (understands semantic meaning)
**Speed:** Moderate (depends on model size)

---

### Source Credibility Weighting

#### **Assigning Source Weights**

```python
SOURCE_CREDIBILITY = {
    'bloomberg': 1.0,
    'reuters': 1.0,
    'wsj': 0.95,
    'cnbc': 0.85,
    'marketwatch': 0.80,
    'seeking_alpha': 0.70,
    'google_news': 0.60,
    'reddit': 0.40,
    'twitter': 0.35,
    'unknown': 0.50
}

def weight_article_sentiment(article, sentiment_score):
    """Apply source credibility weighting"""
    source = article.get('source', 'unknown').lower()
    credibility = SOURCE_CREDIBILITY.get(source, 0.50)

    weighted_sentiment = sentiment_score * credibility

    return {
        'original_sentiment': sentiment_score,
        'weighted_sentiment': weighted_sentiment,
        'source_credibility': credibility
    }
```

---

### Complete Aggregation Pipeline

```python
class FinancialNewsAggregator:
    def __init__(self):
        self.sources = self._initialize_sources()

    def collect_news(self, ticker, hours=24):
        """Collect from all sources"""
        all_news = []

        # RSS feeds
        all_news.extend(self._collect_rss(ticker, hours))

        # APIs
        all_news.extend(self._collect_api(ticker, hours))

        return all_news

    def process_news(self, articles):
        """Complete processing pipeline"""

        # 1. URL deduplication
        articles = deduplicate_urls(articles)

        # 2. TF-IDF deduplication
        articles = deduplicate_tfidf(articles, threshold=0.85)

        # 3. Extract entities
        for article in articles:
            article['entities'] = extract_entities(article['title'])

        # 4. Sentiment analysis
        for article in articles:
            sentiment = get_sentiment(article['title'] + " " + article.get('summary', ''))
            article['sentiment'] = weight_article_sentiment(article, sentiment)

        # 5. Sort by publication time
        articles = sorted(articles, key=lambda x: x['published'], reverse=True)

        return articles

    def aggregate_sentiment(self, articles):
        """Calculate overall sentiment for ticker"""
        if not articles:
            return 0.0

        total_weight = sum(a['sentiment']['source_credibility'] for a in articles)
        weighted_sum = sum(a['sentiment']['weighted_sentiment'] for a in articles)

        return weighted_sum / total_weight if total_weight > 0 else 0.0
```

---

### Implementation Recommendations

**Beginner:**
1. Use finnews or RSS feeds
2. Simple exact title deduplication
3. Basic sentiment averaging

**Intermediate:**
1. Multi-source RSS + API aggregation
2. TF-IDF deduplication
3. Source credibility weighting

**Advanced:**
1. Real-time streaming aggregation
2. Semantic deduplication with transformers
3. Custom source quality scoring
4. Database caching for historical lookups

---

## 8. Temporal Decay of News Impact

### Overview
News impact on stock prices diminishes over time. Incorporating temporal decay weights ensures recent news has more influence than older news in prediction models.

### Academic Findings

**Key Research:**
1. **Immediate Impact:**
   - "Models using only news from the day before forecasting outperform those using news from past day, week, and month"
   - Maximum impact: Day 0-1 after news release

2. **Short-term Decay:**
   - Text impact persists for 1-5 days
   - Most decline occurs within first 24-48 hours

3. **Investor Understanding:**
   - "Investors correctly understand that predictive power of earnings declines over forecasting horizon"
   - Decline pattern: Step function (drops when new news arrives)

**Academic Support:**
- "A comparative study on effect of news sentiment on stock price prediction" (PMC, 2023)
- "LSTM based stock prediction using weighted and categorized financial news" (PMC, 2023)
- "Modeling News Interactions and Influence for Financial Market Prediction" (arXiv, 2024)

---

### Temporal Decay Models

#### **1. Exponential Decay** (Most Common)

**Formula:**
```
weight(t) = e^(-λ * t)

where:
  t = time elapsed since news (in days)
  λ = decay rate parameter (higher = faster decay)
```

**Python Implementation:**
```python
import numpy as np
from datetime import datetime, timedelta

def exponential_decay_weight(news_date, current_date, decay_rate=0.3):
    """
    Calculate exponential decay weight for news

    Args:
        news_date: datetime of news publication
        current_date: datetime of prediction/analysis
        decay_rate: lambda parameter (0.1=slow, 0.5=fast decay)

    Returns:
        float: weight between 0 and 1
    """
    days_elapsed = (current_date - news_date).days
    weight = np.exp(-decay_rate * days_elapsed)
    return weight

# Example
news_date = datetime(2024, 11, 15)
current_date = datetime(2024, 11, 19)

weight = exponential_decay_weight(news_date, current_date, decay_rate=0.3)
print(f"4 days old news weight: {weight:.3f}")  # ~0.301

# Decay curves for different rates
import matplotlib.pyplot as plt

days = np.arange(0, 30)
for decay_rate in [0.1, 0.3, 0.5, 1.0]:
    weights = [np.exp(-decay_rate * d) for d in days]
    plt.plot(days, weights, label=f'λ={decay_rate}')

plt.xlabel('Days Since Publication')
plt.ylabel('Weight')
plt.title('Exponential Decay Curves')
plt.legend()
plt.grid(True)
```

**Recommended Decay Rates:**
- Breaking news / earnings: λ = 0.5 (fast decay)
- General news: λ = 0.3 (moderate decay)
- Long-term trends: λ = 0.1 (slow decay)

**Complexity:** Beginner

---

#### **2. Half-Life Decay**

**Formula:**
```
weight(t) = 0.5^(t / half_life)

where:
  half_life = days until weight drops to 50%
```

**Python Implementation:**
```python
def half_life_decay(news_date, current_date, half_life=2):
    """
    Half-life decay model

    Args:
        half_life: days for weight to decay to 50%
    """
    days_elapsed = (current_date - news_date).days
    weight = 0.5 ** (days_elapsed / half_life)
    return weight

# Example: After 2 days, weight = 0.5
# After 4 days, weight = 0.25
# After 6 days, weight = 0.125
```

**Recommended Half-Lives:**
- High-frequency trading: 0.5-1 day
- Daily predictions: 2-3 days
- Weekly predictions: 5-7 days

**Complexity:** Beginner

---

#### **3. Linear Decay with Floor**

**Formula:**
```
weight(t) = max(floor, 1 - (decay_rate * t))
```

**Python Implementation:**
```python
def linear_decay(news_date, current_date, decay_rate=0.15, floor=0.1):
    """
    Linear decay with minimum weight floor

    Args:
        decay_rate: weight reduction per day
        floor: minimum weight (doesn't decay below this)
    """
    days_elapsed = (current_date - news_date).days
    weight = max(floor, 1.0 - (decay_rate * days_elapsed))
    return weight

# After 3 days: 1 - 0.15*3 = 0.55
# After 7 days: 0.1 (floor reached)
```

**Use Case:** When old news maintains some minimum relevance

**Complexity:** Beginner

---

#### **4. Step Function Decay**

**Description:** Weight drops in steps rather than continuously

**Python Implementation:**
```python
def step_decay(news_date, current_date):
    """
    Step function decay based on research findings
    """
    days = (current_date - news_date).days

    if days == 0:
        return 1.0      # Same day
    elif days == 1:
        return 0.8      # 1 day old
    elif days <= 3:
        return 0.5      # 2-3 days
    elif days <= 7:
        return 0.3      # Up to 1 week
    elif days <= 14:
        return 0.1      # Up to 2 weeks
    else:
        return 0.05     # Older than 2 weeks
```

**Complexity:** Beginner
**Academic Basis:** Matches findings that decay is not smooth but occurs in steps

---

#### **5. Event-Dependent Decay** (Advanced)

**Description:** Decay rate depends on news type

```python
EVENT_DECAY_RATES = {
    'earnings': {
        'lambda': 0.5,
        'half_life': 1.5,
        'description': 'Fast decay - immediate impact'
    },
    'merger': {
        'lambda': 0.1,
        'half_life': 7,
        'description': 'Slow decay - long-term impact'
    },
    'product_launch': {
        'lambda': 0.2,
        'half_life': 5,
        'description': 'Moderate decay'
    },
    'scandal': {
        'lambda': 0.15,
        'half_life': 6,
        'description': 'Moderate to slow decay'
    },
    'general_news': {
        'lambda': 0.3,
        'half_life': 3,
        'description': 'Standard decay'
    }
}

def event_based_decay(news_date, current_date, event_type='general_news'):
    """Apply decay based on event type"""
    decay_params = EVENT_DECAY_RATES.get(event_type, EVENT_DECAY_RATES['general_news'])

    days_elapsed = (current_date - news_date).days
    weight = np.exp(-decay_params['lambda'] * days_elapsed)

    return weight
```

**Complexity:** Advanced
**Performance:** Best accuracy (event-specific decay)

---

### Integration with Sentiment Aggregation

#### **Weighted Sentiment Score**

```python
def calculate_decayed_sentiment(articles, current_date, decay_model='exponential'):
    """
    Calculate sentiment score with temporal decay weighting

    Args:
        articles: List of article dicts with 'sentiment', 'published_date', 'event_type'
        current_date: Date for prediction
        decay_model: 'exponential', 'half_life', 'step', or 'event_based'

    Returns:
        float: Time-weighted sentiment score
    """
    if not articles:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    for article in articles:
        sentiment = article['sentiment']
        published = article['published_date']

        # Calculate temporal weight
        if decay_model == 'exponential':
            time_weight = exponential_decay_weight(published, current_date, decay_rate=0.3)
        elif decay_model == 'half_life':
            time_weight = half_life_decay(published, current_date, half_life=2)
        elif decay_model == 'step':
            time_weight = step_decay(published, current_date)
        elif decay_model == 'event_based':
            event_type = article.get('event_type', 'general_news')
            time_weight = event_based_decay(published, current_date, event_type)

        # Combine with source credibility
        source_weight = article.get('source_credibility', 1.0)
        final_weight = time_weight * source_weight

        weighted_sum += sentiment * final_weight
        total_weight += final_weight

    return weighted_sum / total_weight if total_weight > 0 else 0.0

# Example usage
articles = [
    {
        'sentiment': 0.8,
        'published_date': datetime(2024, 11, 19),
        'source_credibility': 1.0,
        'event_type': 'earnings'
    },
    {
        'sentiment': -0.3,
        'published_date': datetime(2024, 11, 17),
        'source_credibility': 0.8,
        'event_type': 'general_news'
    }
]

current_date = datetime(2024, 11, 19)
score = calculate_decayed_sentiment(articles, current_date, decay_model='event_based')
print(f"Time-weighted sentiment: {score:.3f}")
```

---

### Time Windows for Analysis

#### **Rolling Window Approach**

```python
def get_time_windowed_news(articles, current_date, window_days=7):
    """Filter news within time window"""
    cutoff_date = current_date - timedelta(days=window_days)

    windowed = [
        article for article in articles
        if article['published_date'] >= cutoff_date
    ]

    return windowed

# Multi-window analysis
def multi_window_sentiment(articles, current_date):
    """Calculate sentiment for different time windows"""
    windows = {
        '1day': 1,
        '3day': 3,
        '1week': 7,
        '2week': 14
    }

    results = {}
    for window_name, days in windows.items():
        windowed_articles = get_time_windowed_news(articles, current_date, days)
        sentiment = calculate_decayed_sentiment(windowed_articles, current_date)
        results[window_name] = sentiment

    return results
```

**Use Case:** Compare short-term vs long-term sentiment trends

---

### Academic Research on Temporal Weighting

**Key Papers:**
1. **"LSTM based stock prediction using weighted and categorized financial news" (PMC, 2023)**
   - WCN-LSTM model with temporal weighting
   - Demonstrates improved prediction with time-based news weighting

2. **"From Headlines to Forecasts: Narrative Econometrics in Equity Markets" (MDPI)**
   - Two-part approach: exponential decay + binary activation
   - Distinguishes ongoing vs temporary story effects

3. **"A deep fusion model for stock market prediction" (Neural Computing, 2024)**
   - Deep learning integration with temporal features
   - LSTM/GRU performance significantly improved with time-weighted news

**Consensus:**
- Recent news (0-1 day): Full weight
- Near-term news (2-5 days): Exponential decay
- Older news (5+ days): Minimal weight or exclude
- Event-specific decay improves accuracy

---

### Implementation Recommendations

**Beginner:**
- Use exponential decay with λ=0.3
- 7-day rolling window
- Simple date filtering

**Intermediate:**
- Half-life decay with event-specific parameters
- Multi-window analysis (1day, 3day, 1week)
- Source credibility + temporal weighting

**Advanced:**
- Event-based decay rates
- Step functions matching market behavior
- LSTM integration with temporal features
- Dynamic decay rate learning

---

## 9. News Importance Weighting

### Overview
Not all news is equally important. Weighting news by importance/significance improves sentiment aggregation and prediction accuracy.

### Importance Factors

#### **1. Event Type Importance**

```python
EVENT_IMPORTANCE_WEIGHTS = {
    # High impact events
    'earnings': 1.0,
    'merger_acquisition': 1.0,
    'fda_approval': 0.95,
    'ceo_change': 0.9,
    'dividend_change': 0.85,

    # Medium impact
    'product_launch': 0.7,
    'partnership': 0.65,
    'analyst_upgrade': 0.6,
    'guidance_change': 0.75,

    # Lower impact
    'general_news': 0.4,
    'opinion': 0.3,
    'rumor': 0.2,
}

def get_event_importance(event_type):
    """Return importance weight for event type"""
    return EVENT_IMPORTANCE_WEIGHTS.get(event_type, 0.5)
```

**Academic Support:**
- "More important events like US election can strongly affect algorithm performance"
- "There should be a way to identify strength of each news"

---

#### **2. Source Credibility**

```python
SOURCE_IMPORTANCE = {
    # Tier 1: Authoritative financial sources
    'bloomberg': 1.0,
    'reuters': 1.0,
    'wsj': 0.95,
    'financial_times': 0.95,

    # Tier 2: Major business news
    'cnbc': 0.85,
    'marketwatch': 0.80,
    'barrons': 0.85,

    # Tier 3: Specialized financial
    'seeking_alpha': 0.70,
    'benzinga': 0.65,
    'motley_fool': 0.60,

    # Tier 4: General news
    'google_news': 0.50,
    'yahoo_finance': 0.55,

    # Tier 5: Social media
    'reddit': 0.30,
    'twitter': 0.25,
    'stocktwits': 0.35,
}
```

---

#### **3. TF-IDF Word Importance**

**Description:** Words with high TF-IDF scores indicate more significant news

**Python Implementation:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

class NewsImportanceScorer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)  # Unigrams and bigrams
        )
        self.is_fitted = False

    def fit(self, news_corpus):
        """Fit TF-IDF on historical news corpus"""
        texts = [f"{n['title']} {n.get('summary', '')}" for n in news_corpus]
        self.vectorizer.fit(texts)
        self.is_fitted = True

    def score_importance(self, article):
        """Score article importance based on TF-IDF"""
        if not self.is_fitted:
            return 0.5  # Default

        text = f"{article['title']} {article.get('summary', '')}"
        tfidf_vector = self.vectorizer.transform([text])

        # Average TF-IDF score as importance
        importance = tfidf_vector.mean()

        # Normalize to 0-1 range
        return min(1.0, importance * 2)  # Scale factor

# Usage
scorer = NewsImportanceScorer()
scorer.fit(historical_news)  # Fit on past news

for article in new_articles:
    importance = scorer.score_importance(article)
    article['tfidf_importance'] = importance
```

**Complexity:** Intermediate
**Accuracy:** Good for identifying unusual/significant content

**Academic Support:**
- "TF-IDF allocates weight to words based on frequency and prominence"
- "Captures relevance of each word in headlines for accurate prediction"

---

#### **4. Market Reaction-Based Importance**

**Description:** Learn importance from historical price reactions

```python
def calculate_historical_impact(article, ticker, price_data):
    """
    Calculate how much article type affected price in past

    Returns importance score based on historical correlation
    """
    event_type = article['event_type']
    published_date = article['published_date']

    # Get price change after news
    try:
        t0_price = price_data.loc[published_date, 'Close']
        t1_price = price_data.loc[published_date + timedelta(days=1), 'Close']
        price_change = (t1_price - t0_price) / t0_price
    except:
        return 0.5  # Default if data unavailable

    # Absolute price change as importance indicator
    importance = min(1.0, abs(price_change) * 10)  # Scale factor

    return importance
```

**Complexity:** Advanced
**Accuracy:** Best (data-driven)
**Limitation:** Requires historical correlation analysis

---

#### **5. Engagement Metrics**

**Social Media Importance:**
```python
def social_engagement_importance(article):
    """
    Calculate importance from social metrics

    Factors: shares, likes, comments, retweets
    """
    shares = article.get('shares', 0)
    likes = article.get('likes', 0)
    comments = article.get('comments', 0)

    # Weighted engagement score
    engagement_score = (shares * 2 + likes * 1 + comments * 1.5)

    # Normalize (log scale for viral posts)
    if engagement_score > 0:
        importance = min(1.0, np.log10(engagement_score + 1) / 5)
    else:
        importance = 0.1

    return importance
```

**Use Case:** Reddit, Twitter, StockTwits
**Complexity:** Beginner (if metrics available)

---

#### **6. Named Entity Importance**

**Description:** Articles mentioning key people/events are more important

```python
IMPORTANT_ENTITIES = {
    'people': ['Jerome Powell', 'Janet Yellen', 'Elon Musk', 'Tim Cook'],
    'organizations': ['Federal Reserve', 'SEC', 'FDA'],
    'events': ['earnings call', 'merger', 'acquisition', 'IPO']
}

def entity_importance_score(article):
    """Boost importance if important entities mentioned"""
    text = f"{article['title']} {article.get('summary', '')}".lower()

    importance_boost = 0.0

    # Check for important people
    for person in IMPORTANT_ENTITIES['people']:
        if person.lower() in text:
            importance_boost += 0.2

    # Check for organizations
    for org in IMPORTANT_ENTITIES['organizations']:
        if org.lower() in text:
            importance_boost += 0.15

    # Check for event keywords
    for event in IMPORTANT_ENTITIES['events']:
        if event.lower() in text:
            importance_boost += 0.1

    return min(1.0, 0.5 + importance_boost)  # Base 0.5 + boosts
```

**Complexity:** Intermediate

---

### Composite Importance Score

#### **Weighted Multi-Factor Model**

```python
class NewsImportanceCalculator:
    """Calculate comprehensive importance score from multiple factors"""

    def __init__(self, weights=None):
        # Default weights for different factors
        self.weights = weights or {
            'event_type': 0.25,
            'source_credibility': 0.20,
            'tfidf': 0.15,
            'entities': 0.15,
            'engagement': 0.15,
            'historical_impact': 0.10
        }

    def calculate_importance(self, article, historical_data=None):
        """
        Calculate composite importance score

        Args:
            article: Article dict with metadata
            historical_data: Optional price data for impact analysis

        Returns:
            float: Importance score 0-1
        """
        scores = {}

        # 1. Event type importance
        event_type = article.get('event_type', 'general_news')
        scores['event_type'] = EVENT_IMPORTANCE_WEIGHTS.get(event_type, 0.5)

        # 2. Source credibility
        source = article.get('source', 'unknown')
        scores['source_credibility'] = SOURCE_IMPORTANCE.get(source, 0.5)

        # 3. TF-IDF importance (if available)
        scores['tfidf'] = article.get('tfidf_importance', 0.5)

        # 4. Entity importance
        scores['entities'] = entity_importance_score(article)

        # 5. Engagement (if available)
        scores['engagement'] = social_engagement_importance(article)

        # 6. Historical impact (if data provided)
        if historical_data:
            scores['historical_impact'] = calculate_historical_impact(
                article, article['ticker'], historical_data
            )
        else:
            scores['historical_impact'] = 0.5

        # Calculate weighted average
        total_importance = sum(
            scores[factor] * self.weights[factor]
            for factor in self.weights.keys()
        )

        return total_importance

# Usage
importance_calc = NewsImportanceCalculator()

for article in articles:
    importance = importance_calc.calculate_importance(article, historical_price_data)
    article['importance_score'] = importance
```

---

### Integration: Sentiment with Importance

#### **Final Weighted Sentiment Formula**

```python
def calculate_final_sentiment(articles, current_date):
    """
    Calculate sentiment with all weighting factors:
    - Source credibility
    - Temporal decay
    - News importance
    """
    if not articles:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    importance_calc = NewsImportanceCalculator()

    for article in articles:
        # Base sentiment score (-1 to 1)
        sentiment = article['sentiment']

        # Importance weight (0-1)
        importance = importance_calc.calculate_importance(article)

        # Temporal decay weight (0-1)
        time_weight = exponential_decay_weight(
            article['published_date'],
            current_date,
            decay_rate=0.3
        )

        # Source credibility (0-1)
        source_credibility = article.get('source_credibility', 1.0)

        # Combined weight
        final_weight = importance * time_weight * source_credibility

        # Weighted contribution
        weighted_sum += sentiment * final_weight
        total_weight += final_weight

    # Normalized sentiment
    final_sentiment = weighted_sum / total_weight if total_weight > 0 else 0.0

    return final_sentiment, total_weight  # Return weight for confidence measure
```

---

### Weighted Sentiment Index (Tweighted)

**Research-Based Approach:**

```python
def calculate_tweighted_index(articles):
    """
    Novel weighted sentiment index from research
    Combines VADER sentiment with extracted features
    """
    indices = []

    for article in articles:
        # Get VADER scores
        vader_compound = article['vader_compound']  # -1 to 1

        # Extract features
        has_ticker_mention = 1 if article.get('ticker_mentions') else 0
        source_tier = get_source_tier(article['source'])  # 1-5
        word_count = len(article['text'].split())
        has_numbers = 1 if re.search(r'\d+', article['text']) else 0

        # Weighted index formula (example)
        tweighted = (
            vader_compound * 0.5 +
            has_ticker_mention * 0.2 +
            (6 - source_tier) * 0.1 +  # Lower tier number = better
            min(word_count / 500, 1.0) * 0.1 +  # Longer = more important
            has_numbers * 0.1  # Financial numbers present
        )

        indices.append(tweighted)

    return np.mean(indices) if indices else 0.0
```

**Academic Support:**
- "Researchers combine VADER sentiment with extracted tweet features to generate novel weighted sentiment index Tweighted"

---

### Categorical News Weighting (WCN-LSTM)

**Research Approach:**

```python
NEWS_CATEGORIES = {
    'company_specific': {
        'examples': ['earnings', 'product_launch', 'management'],
        'weight': 1.0
    },
    'sector_news': {
        'examples': ['industry trends', 'competitor news'],
        'weight': 0.7
    },
    'macro_economic': {
        'examples': ['fed_news', 'gdp', 'unemployment'],
        'weight': 0.5
    }
}

def categorize_and_weight_news(articles, ticker):
    """
    Categorize news by area of influence
    Apply optimized weights from WCN-LSTM research
    """
    categorized = {cat: [] for cat in NEWS_CATEGORIES.keys()}

    for article in articles:
        category = classify_news_category(article, ticker)
        categorized[category].append(article)

    # Calculate weighted sentiment per category
    category_sentiments = {}
    for category, cat_articles in categorized.items():
        if cat_articles:
            avg_sentiment = np.mean([a['sentiment'] for a in cat_articles])
            weight = NEWS_CATEGORIES[category]['weight']
            category_sentiments[category] = avg_sentiment * weight

    # Overall weighted sentiment
    return sum(category_sentiments.values())
```

**Academic Support:**
- "WCN-LSTM strengthens prediction by using weighted news sentiment scores for different categories"
- "Financial news categorized into three groups according to stock market structural hierarchy"

---

### Implementation Recommendations

**Beginner:**
1. Use event type weights (simple lookup)
2. Source credibility weighting
3. Simple averaging

**Intermediate:**
1. Multi-factor importance (event + source + TF-IDF)
2. Categorical weighting
3. Engagement metrics (if available)

**Advanced:**
1. Machine learning for importance prediction
2. Historical impact correlation
3. Dynamic weight optimization
4. WCN-LSTM categorical approach

---

## 10. Integration Architecture: Combining Qualitative & Quantitative

### Overview
The most effective stock prediction systems combine:
- **Qualitative:** News sentiment, social media, events
- **Quantitative:** Price history, technical indicators, volume

### Hybrid Model Architectures

#### **Architecture 1: Feature Concatenation**

**Description:** Combine features before feeding to model

```
┌─────────────────┐
│  News Articles  │
└────────┬────────┘
         │
    ┌────▼────────┐
    │  Sentiment  │
    │  Analysis   │
    │  (FinBERT)  │
    └────┬────────┘
         │
    ┌────▼──────────────┐         ┌──────────────────┐
    │ Sentiment Features│         │ Price History    │
    │ - Daily sentiment │         │ - Close, Open    │
    │ - Event scores    │◄────────┤ - Volume         │
    │ - Source weights  │         │ - Tech Indicators│
    └────┬──────────────┘         └──────────────────┘
         │
    ┌────▼────────┐
    │ Concatenate │
    │   Features  │
    └────┬────────┘
         │
    ┌────▼────────┐
    │ LSTM / GRU  │
    │   Model     │
    └────┬────────┘
         │
    ┌────▼────────┐
    │ Prediction  │
    └─────────────┘
```

**Python Implementation:**
```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Concatenate, Input
from tensorflow.keras.models import Model

class HybridStockPredictor:
    def __init__(self, lookback=60):
        self.lookback = lookback
        self.scaler_price = StandardScaler()
        self.scaler_sentiment = StandardScaler()

    def prepare_features(self, price_data, sentiment_data, ticker):
        """Prepare hybrid features"""

        # Quantitative features
        price_features = pd.DataFrame({
            'close': price_data['Close'],
            'open': price_data['Open'],
            'high': price_data['High'],
            'low': price_data['Low'],
            'volume': price_data['Volume'],

            # Technical indicators
            'sma_20': price_data['Close'].rolling(20).mean(),
            'sma_50': price_data['Close'].rolling(50).mean(),
            'rsi': self.calculate_rsi(price_data['Close']),
            'macd': self.calculate_macd(price_data['Close']),
        })

        # Qualitative features
        sentiment_features = pd.DataFrame({
            'daily_sentiment': sentiment_data['weighted_sentiment'],
            'sentiment_volume': sentiment_data['article_count'],
            'positive_ratio': sentiment_data['positive_ratio'],
            'event_importance': sentiment_data['avg_importance'],
        })

        # Align dates
        combined = pd.concat([price_features, sentiment_features], axis=1)
        combined = combined.dropna()

        return combined

    def create_sequences(self, data, target_col='close'):
        """Create sequences for LSTM"""
        X, y = [], []

        for i in range(self.lookback, len(data)):
            X.append(data[i-self.lookback:i])
            y.append(data[i][target_col])

        return np.array(X), np.array(y)

    def build_model(self, feature_dim):
        """Build hybrid LSTM model"""
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(self.lookback, feature_dim)),
            Dropout(0.2),
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)  # Price prediction
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

# Usage
predictor = HybridStockPredictor(lookback=60)

# Get data
price_data = yf.download('AAPL', start='2020-01-01', end='2024-12-01')
sentiment_data = get_daily_sentiment('AAPL', start='2020-01-01', end='2024-12-01')

# Prepare features
features = predictor.prepare_features(price_data, sentiment_data, 'AAPL')

# Create sequences
X, y = predictor.create_sequences(features)

# Train
model = predictor.build_model(feature_dim=features.shape[1])
model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2)
```

**Complexity:** Intermediate to Advanced
**Performance:** Good (10-20% improvement over price-only models)

---

#### **Architecture 2: Dual-Stream with Late Fusion**

**Description:** Separate processing paths, combined at decision layer

```
News Stream:                    Price Stream:
┌──────────┐                   ┌──────────┐
│  News    │                   │  Price   │
│ Articles │                   │  Data    │
└────┬─────┘                   └────┬─────┘
     │                              │
┌────▼─────┐                   ┌────▼─────┐
│ FinBERT  │                   │  LSTM    │
│ Encoding │                   │ Features │
└────┬─────┘                   └────┬─────┘
     │                              │
┌────▼─────┐                   ┌────▼─────┐
│  LSTM    │                   │  Dense   │
│ (64 dim) │                   │ (64 dim) │
└────┬─────┘                   └────┬─────┘
     │                              │
     └────────┬──────────────────────┘
              │
         ┌────▼─────┐
         │ Concat   │
         │ (128 dim)│
         └────┬─────┘
              │
         ┌────▼─────┐
         │  Dense   │
         │  Layers  │
         └────┬─────┘
              │
         ┌────▼─────┐
         │Prediction│
         └──────────┘
```

**Python Implementation:**
```python
from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate
from tensorflow.keras.models import Model

def build_dual_stream_model(price_seq_len, sentiment_seq_len,
                            price_features, sentiment_features):
    """
    Dual-stream architecture with late fusion
    """
    # Price stream
    price_input = Input(shape=(price_seq_len, price_features), name='price_input')
    price_lstm = LSTM(64, return_sequences=False)(price_input)
    price_dense = Dense(64, activation='relu')(price_lstm)

    # Sentiment stream
    sentiment_input = Input(shape=(sentiment_seq_len, sentiment_features),
                           name='sentiment_input')
    sentiment_lstm = LSTM(64, return_sequences=False)(sentiment_input)
    sentiment_dense = Dense(64, activation='relu')(sentiment_lstm)

    # Fusion layer
    concatenated = Concatenate()([price_dense, sentiment_dense])

    # Decision layers
    fusion_dense1 = Dense(128, activation='relu')(concatenated)
    fusion_dropout = Dropout(0.3)(fusion_dense1)
    fusion_dense2 = Dense(64, activation='relu')(fusion_dropout)

    # Output
    output = Dense(1, activation='linear', name='price_prediction')(fusion_dense2)

    # Create model
    model = Model(inputs=[price_input, sentiment_input], outputs=output)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    return model

# Usage
model = build_dual_stream_model(
    price_seq_len=60,
    sentiment_seq_len=30,
    price_features=9,
    sentiment_features=4
)

# Train with dual inputs
history = model.fit(
    {'price_input': X_price, 'sentiment_input': X_sentiment},
    y_target,
    epochs=50,
    batch_size=32,
    validation_split=0.2
)
```

**Complexity:** Advanced
**Performance:** Best (allows each stream to learn independently)

---

#### **Architecture 3: FinBERT-LSTM (Research-Backed)**

**Description:** From academic papers (arXiv:2407.16150)

**Implementation:**
```python
from transformers import BertTokenizer, BertModel
import torch
import torch.nn as nn

class FinBERTLSTMPredictor(nn.Module):
    def __init__(self, lstm_hidden=128, num_layers=2):
        super(FinBERTLSTMPredictor, self).__init__()

        # FinBERT for news embedding
        self.finbert = BertModel.from_pretrained('yiyanghkust/finbert-tone')

        # Freeze FinBERT (optional - faster training)
        for param in self.finbert.parameters():
            param.requires_grad = False

        # LSTM for time series
        self.lstm = nn.LSTM(
            input_size=768 + 10,  # FinBERT embedding (768) + price features (10)
            hidden_size=lstm_hidden,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        # Prediction head
        self.fc = nn.Sequential(
            nn.Linear(lstm_hidden, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1)
        )

    def forward(self, news_text, price_features):
        # Encode news with FinBERT
        with torch.no_grad():
            news_embeddings = self.finbert(**news_text).last_hidden_state[:, 0, :]

        # Combine news embeddings with price features
        combined = torch.cat([news_embeddings, price_features], dim=1)

        # LSTM processing
        lstm_out, _ = self.lstm(combined.unsqueeze(1))

        # Prediction
        prediction = self.fc(lstm_out[:, -1, :])

        return prediction

# Usage
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
model = FinBERTLSTMPredictor()

# Prepare data
news_text = tokenizer(news_headlines, padding=True, truncation=True,
                      return_tensors='pt')
price_features = torch.tensor(technical_indicators)

# Predict
prediction = model(news_text, price_features)
```

**Academic Support:**
- "FinBERT-LSTM performs best, followed by standalone LSTM, with DNN models ranking third" (2024)
- Tested on NASDAQ-100 stocks

---

### Feature Engineering

#### **Quantitative Features**

```python
def calculate_technical_indicators(price_data):
    """Calculate technical indicators"""
    df = price_data.copy()

    # Moving averages
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['sma_50'] = df['Close'].rolling(window=50).mean()
    df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['bb_middle'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (std * 2)
    df['bb_lower'] = df['bb_middle'] - (std * 2)

    # Volume indicators
    df['volume_sma'] = df['Volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma']

    # Price momentum
    df['momentum'] = df['Close'] - df['Close'].shift(10)
    df['roc'] = ((df['Close'] - df['Close'].shift(10)) /
                 df['Close'].shift(10)) * 100

    return df
```

---

#### **Qualitative Features**

```python
def calculate_sentiment_features(articles, date_range):
    """Calculate sentiment features from news"""
    features = []

    for date in date_range:
        # Get articles for this date
        daily_articles = [a for a in articles
                         if a['published_date'].date() == date]

        if not daily_articles:
            # No news day
            features.append({
                'date': date,
                'sentiment_mean': 0,
                'sentiment_std': 0,
                'article_count': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'importance_mean': 0,
                'source_quality_mean': 0.5
            })
            continue

        sentiments = [a['sentiment'] for a in daily_articles]
        importances = [a['importance_score'] for a in daily_articles]
        sources = [a['source_credibility'] for a in daily_articles]

        features.append({
            'date': date,
            'sentiment_mean': np.mean(sentiments),
            'sentiment_std': np.std(sentiments),
            'article_count': len(daily_articles),
            'positive_ratio': sum(s > 0 for s in sentiments) / len(sentiments),
            'negative_ratio': sum(s < 0 for s in sentiments) / len(sentiments),
            'importance_mean': np.mean(importances),
            'source_quality_mean': np.mean(sources),
            'max_abs_sentiment': max(abs(s) for s in sentiments),
        })

    return pd.DataFrame(features)
```

---

### Academic Research on Hybrid Models

**Key Papers:**

1. **"Hybrid Model based on unification of Technical Analysis and Sentiment Analysis"** (ResearchGate, 2018)
   - Combines PMI sentiment features with technical indicators
   - SVM regression for prediction

2. **"A deep fusion model for stock market prediction with news headlines and time series"** (Springer, 2024)
   - Multimodal deep fusion
   - LSTM + BERT architecture
   - 8-12% accuracy improvement

3. **"A hybrid model integrating deep learning with investor sentiment"** (ScienceDirect, 2021)
   - LSTM for technical + sentiment features
   - Strong evidence for predictive power

4. **"Stock trend prediction using sentiment analysis"** (PeerJ, 2023)
   - Sentiment classification provides additional predictive power over technical alone
   - 20% accuracy improvement with sentiment

**Consensus Findings:**
- Hybrid models outperform single-modality approaches
- Best architecture: Deep learning (LSTM/GRU) with both data types
- Sentiment adds 10-20% relative improvement
- Most effective for short-term prediction (1-5 days)

---

### Performance Metrics

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

def evaluate_predictions(y_true, y_pred):
    """Comprehensive evaluation metrics"""

    # Regression metrics
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Direction accuracy
    true_direction = np.sign(np.diff(y_true))
    pred_direction = np.sign(np.diff(y_pred))
    direction_accuracy = np.mean(true_direction == pred_direction)

    # Financial metrics
    returns_true = np.diff(y_true) / y_true[:-1]
    returns_pred = np.diff(y_pred) / y_pred[:-1]

    # Sharpe ratio (if using for trading)
    sharpe = np.mean(returns_pred) / np.std(returns_pred) * np.sqrt(252)

    return {
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'direction_accuracy': direction_accuracy,
        'sharpe_ratio': sharpe
    }
```

---

### Implementation Recommendations

**Beginner:**
1. Start with simple feature concatenation
2. Use scikit-learn RandomForest or XGBoost
3. Basic technical indicators + VADER sentiment
4. Focus on getting pipeline working end-to-end

**Intermediate:**
1. LSTM with combined features
2. FinBERT for sentiment
3. Comprehensive technical indicators
4. Time-weighted and importance-weighted sentiment

**Advanced:**
1. Dual-stream architecture with late fusion
2. FinBERT-LSTM or transformer-based models
3. Multi-task learning (price + direction + volatility)
4. Attention mechanisms for news importance
5. Ensemble of multiple hybrid models

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Objectives:**
- Set up data collection pipeline
- Implement basic sentiment analysis
- Create simple prediction baseline

**Tasks:**
1. **Data Collection:**
   ```python
   # Set up yfinance for price data
   # Set up Google News RSS + Alpha Vantage for news
   # Create database schema (SQLite or PostgreSQL)
   ```

2. **Sentiment Analysis:**
   ```python
   # Implement VADER for quick baseline
   # Test FinBERT on sample news
   # Compare results
   ```

3. **Basic Model:**
   ```python
   # Simple LSTM on price data only (baseline)
   # Measure performance metrics
   ```

**Deliverables:**
- Working data pipeline
- Baseline model accuracy metrics
- Database with historical data

---

### Phase 2: News Integration (Weeks 3-4)

**Objectives:**
- Integrate news sentiment with price prediction
- Implement importance weighting
- Add temporal decay

**Tasks:**
1. **News Processing:**
   ```python
   # Implement news deduplication (TF-IDF)
   # Add NER for ticker extraction
   # Create daily sentiment aggregation
   ```

2. **Feature Engineering:**
   ```python
   # Combine sentiment features with technical indicators
   # Implement temporal decay weighting
   # Add event classification
   ```

3. **Hybrid Model V1:**
   ```python
   # Feature concatenation approach
   # Train LSTM with combined features
   # Evaluate vs baseline
   ```

**Deliverables:**
- News-augmented model
- Comparison metrics (hybrid vs baseline)

---

### Phase 3: Advanced Features (Weeks 5-6)

**Objectives:**
- Implement advanced NLP models
- Add social media sentiment
- Optimize weighting schemes

**Tasks:**
1. **Advanced Sentiment:**
   ```python
   # Deploy FinBERT for production
   # Add GPT-4 for critical news (optional)
   # Implement multi-factor importance scoring
   ```

2. **Social Media:**
   ```python
   # Set up Reddit data collection (PRAW)
   # Add Twitter sentiment (if budget allows)
   # Implement social engagement weighting
   ```

3. **Optimization:**
   ```python
   # Tune decay rates
   # Optimize importance weights
   # A/B test different architectures
   ```

**Deliverables:**
- Production-grade sentiment pipeline
- Social media integration
- Optimized model

---

### Phase 4: Production & Monitoring (Weeks 7-8)

**Objectives:**
- Deploy model for real-time predictions
- Set up monitoring
- Create backtesting framework

**Tasks:**
1. **Deployment:**
   ```python
   # API for predictions
   # Real-time news streaming
   # Automated retraining pipeline
   ```

2. **Monitoring:**
   ```python
   # Track prediction accuracy over time
   # Monitor data drift
   # Alert system for model degradation
   ```

3. **Backtesting:**
   ```python
   # Historical simulation
   # Trading strategy evaluation
   # Risk metrics calculation
   ```

**Deliverables:**
- Production system
- Monitoring dashboards
- Backtest results

---

### Recommended Tech Stack

**Data Collection:**
- `yfinance`: Stock price data (free)
- `feedparser`: RSS feeds (free)
- `alpha_vantage`: News API (free tier)
- `praw`: Reddit data (free)

**NLP:**
- `transformers`: FinBERT, BERT models
- `nltk`: VADER sentiment
- `spacy`: NER, text processing
- `sentence-transformers`: Semantic similarity

**Machine Learning:**
- `tensorflow`/`pytorch`: Deep learning
- `scikit-learn`: Traditional ML, preprocessing
- `xgboost`: Gradient boosting (good baseline)

**Data Management:**
- `pandas`: Data manipulation
- `sqlalchemy`: Database ORM
- `PostgreSQL` or `SQLite`: Database

**Deployment:**
- `fastapi`: REST API
- `docker`: Containerization
- `airflow`: Workflow orchestration
- `mlflow`: Experiment tracking

---

### Cost Estimate (Monthly)

**Free Tier:**
- yfinance: Free
- Google News RSS: Free
- Alpha Vantage: Free (500/day)
- VADER/FinBERT: Free
- Reddit (PRAW): Free
- **Total: $0/month**

**Budget Tier ($50-100/month):**
- NewsAPI Pro: ~$449/month (skip if over budget)
- Alpha Vantage Premium: $49/month
- Twitter API Basic: $100/month
- OpenAI API (GPT-4): ~$20-50/month (limited usage)
- **Total: ~$70-100/month** (without NewsAPI)

**Production Tier ($200-500/month):**
- Financial Modeling Prep: $14-50/month
- Benzinga News API: ~$100/month
- Twitter API: $100/month
- OpenAI API: $50-100/month
- Cloud hosting (AWS/GCP): $50-100/month
- **Total: $314-450/month**

---

### Success Metrics

**Technical:**
- Direction accuracy: >55% (baseline: 50%)
- RMSE: <5% of stock price
- Sharpe ratio: >1.0 (if trading)

**Business:**
- Prediction latency: <5 seconds
- Data pipeline uptime: >99%
- News processing: Real-time (<1 min delay)

**Academic Benchmarks:**
- 10-20% improvement over price-only baseline
- Comparable to published research results

---

## Summary & Key Takeaways

### Best Practices

1. **Start Simple:**
   - Begin with VADER + basic LSTM
   - Add complexity incrementally
   - Measure impact of each addition

2. **Data Quality > Model Complexity:**
   - Clean, deduplicated news is critical
   - Source credibility weighting essential
   - Temporal decay significantly impacts accuracy

3. **Combine Multiple Signals:**
   - No single source is sufficient
   - Hybrid quantitative + qualitative > either alone
   - Ensemble models often outperform single models

4. **Domain-Specific Models:**
   - FinBERT > VADER for accuracy
   - VADER > FinBERT for speed/cost
   - GPT-4 best for complex analysis (expensive)

5. **Realistic Expectations:**
   - Sentiment adds 10-20% improvement (not 100%)
   - Best for short-term prediction (1-5 days)
   - Market efficiency limits predictability

---

### Quick Reference: Library Selection

| Use Case | Recommended Tools |
|----------|------------------|
| **Sentiment Analysis** | FinBERT (accuracy) or VADER (speed) |
| **News Collection** | yfinance + Google News RSS (free) or Alpha Vantage (paid) |
| **Social Media** | PRAW (Reddit), avoid Twitter unless budget allows |
| **NER** | spaCy (production) or Hugging Face (accuracy) |
| **Deduplication** | TF-IDF (sklearn) or Sentence Transformers (advanced) |
| **Prediction Model** | LSTM (Keras/PyTorch) or XGBoost (baseline) |
| **Event Detection** | Zero-shot classification (Hugging Face) |

---

### Academic References

**Key Papers:**
1. Predicting Stock Prices with FinBERT-LSTM (arXiv:2407.16150, 2024)
2. Stock trend prediction using sentiment analysis (PeerJ CS, 2023)
3. News sensitive stock market prediction: literature review (PMC, 2021)
4. On the Importance of Text Analysis for Stock Price Prediction (Stanford NLP, 2014)
5. LSTM based stock prediction using weighted and categorized financial news (PMC, 2023)

**Consensus Findings:**
- Text analysis boosts prediction >10% relative to financial features alone
- Impact persists 1-5 days
- Hybrid deep learning models (LSTM + FinBERT) perform best
- Temporal decay and importance weighting significantly improve results
- Sentiment most effective for short-term predictions

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Maintained By:** Financial Apps Research Team
