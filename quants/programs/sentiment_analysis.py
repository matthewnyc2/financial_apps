"""
Sentiment Analysis for Trading
Implements news sentiment, social media sentiment analysis, FinBERT integration,
and aggregate sentiment indices for trading signals.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
from collections import defaultdict

warnings.filterwarnings('ignore')

# VADER Sentiment Analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Transformers for FinBERT
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers library not installed. FinBERT features limited.")


class VADERSentimentAnalyzer:
    """VADER-based sentiment analysis for news and social media."""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_text(self, text):
        """
        Analyze sentiment using VADER.

        Parameters:
        text: Input text string

        Returns:
        dict with sentiment scores (positive, negative, neutral, compound)
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'compound': 0.0
            }

        scores = self.analyzer.polarity_scores(text)
        return {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'compound': scores['compound']
        }

    def get_sentiment_label(self, compound_score):
        """
        Convert compound score to sentiment label.

        Parameters:
        compound_score: VADER compound score (-1 to 1)

        Returns:
        str: 'positive', 'negative', or 'neutral'
        """
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'


class FinBERTSentimentAnalyzer:
    """FinBERT-based sentiment analysis for financial texts."""

    def __init__(self, model_name='ProsusAI/finbert'):
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            self.available = True
        except Exception as e:
            print(f"FinBERT model loading failed: {e}")
            self.available = False

    def analyze_text(self, text, max_length=512):
        """
        Analyze sentiment using FinBERT.

        Parameters:
        text: Input text string
        max_length: Max token length

        Returns:
        dict with sentiment scores
        """
        if not self.available or not isinstance(text, str):
            return {
                'sentiment': 'neutral',
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'confidence': 0.0
            }

        try:
            inputs = self.tokenizer(
                text[:max_length],
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=max_length
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1)
                probs = probs.cpu().numpy()[0]

            labels = ['negative', 'neutral', 'positive']
            sentiment_idx = np.argmax(probs)

            return {
                'sentiment': labels[sentiment_idx],
                'negative': float(probs[0]),
                'neutral': float(probs[1]),
                'positive': float(probs[2]),
                'confidence': float(probs[sentiment_idx])
            }
        except Exception as e:
            print(f"FinBERT analysis error: {e}")
            return {
                'sentiment': 'neutral',
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'confidence': 0.0
            }


class NewsSentimentScorer:
    """Score sentiment from news articles and financial news."""

    def __init__(self, use_finbert=False):
        self.vader_analyzer = VADERSentimentAnalyzer()
        self.finbert_analyzer = FinBERTSentimentAnalyzer() if (use_finbert and HAS_TRANSFORMERS) else None
        self.news_history = []

    def score_article(self, headline, content, source=None, timestamp=None):
        """
        Score sentiment of a news article.

        Parameters:
        headline: Article headline
        content: Article content/body
        source: News source (e.g., Reuters, Bloomberg)
        timestamp: Publication timestamp

        Returns:
        dict with sentiment scores
        """
        # Combine headline and content for analysis
        full_text = f"{headline} {content}" if content else headline

        # VADER analysis
        vader_scores = self.vader_analyzer.analyze_text(full_text)

        # FinBERT analysis (if available)
        finbert_scores = None
        if self.finbert_analyzer and self.finbert_analyzer.available:
            finbert_scores = self.finbert_analyzer.analyze_text(headline)

        # Headline analysis (often more impactful)
        headline_vader = self.vader_analyzer.analyze_text(headline)

        result = {
            'timestamp': timestamp or datetime.now(),
            'source': source,
            'headline': headline,
            'vader_compound': vader_scores['compound'],
            'vader_positive': vader_scores['positive'],
            'vader_negative': vader_scores['negative'],
            'vader_neutral': vader_scores['neutral'],
            'headline_compound': headline_vader['compound'],
            'finbert_scores': finbert_scores
        }

        # Calculate combined sentiment score
        if finbert_scores:
            result['combined_sentiment'] = (
                0.6 * vader_scores['compound'] +
                0.4 * (finbert_scores['positive'] - finbert_scores['negative'])
            )
        else:
            result['combined_sentiment'] = vader_scores['compound']

        self.news_history.append(result)
        return result

    def aggregate_sentiment(self, lookback_hours=24):
        """
        Aggregate sentiment over time period.

        Parameters:
        lookback_hours: Hours to look back

        Returns:
        dict with aggregate sentiment metrics
        """
        if not self.news_history:
            return {
                'avg_sentiment': 0.0,
                'sentiment_std': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'sentiment_momentum': 0.0
            }

        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        recent = [n for n in self.news_history
                 if n['timestamp'] >= cutoff_time]

        if not recent:
            return {
                'avg_sentiment': 0.0,
                'sentiment_std': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'sentiment_momentum': 0.0
            }

        sentiments = [n['combined_sentiment'] for n in recent]

        positive = sum(1 for s in sentiments if s > 0.05)
        negative = sum(1 for s in sentiments if s < -0.05)
        neutral = len(sentiments) - positive - negative

        # Sentiment momentum: trend in recent vs older
        if len(sentiments) > 5:
            recent_half = sentiments[-len(sentiments)//2:]
            older_half = sentiments[:-len(sentiments)//2]
            momentum = np.mean(recent_half) - np.mean(older_half)
        else:
            momentum = 0.0

        return {
            'avg_sentiment': np.mean(sentiments),
            'sentiment_std': np.std(sentiments),
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'total_articles': len(sentiments),
            'sentiment_momentum': momentum,
            'positive_ratio': positive / len(sentiments) if sentiments else 0
        }


class SocialMediaSentimentAnalyzer:
    """Analyze sentiment from Twitter, Reddit, and other social media."""

    def __init__(self):
        self.vader_analyzer = VADERSentimentAnalyzer()
        self.posts = []

    def analyze_tweet(self, text, engagement_metrics=None, timestamp=None):
        """
        Analyze sentiment from a tweet.

        Parameters:
        text: Tweet text
        engagement_metrics: dict with likes, retweets, replies counts
        timestamp: Tweet timestamp

        Returns:
        dict with sentiment and engagement-weighted score
        """
        sentiment = self.vader_analyzer.analyze_text(text)

        # Default engagement metrics
        if engagement_metrics is None:
            engagement_metrics = {'likes': 0, 'retweets': 0, 'replies': 0}

        # Calculate engagement weight (logarithmic)
        total_engagement = (
            engagement_metrics.get('likes', 0) * 1 +
            engagement_metrics.get('retweets', 0) * 2 +
            engagement_metrics.get('replies', 0) * 1.5
        )
        engagement_weight = np.log1p(total_engagement)

        result = {
            'timestamp': timestamp or datetime.now(),
            'text': text,
            'sentiment_score': sentiment['compound'],
            'positive': sentiment['positive'],
            'negative': sentiment['negative'],
            'neutral': sentiment['neutral'],
            'engagement_metrics': engagement_metrics,
            'engagement_weight': engagement_weight,
            'weighted_sentiment': sentiment['compound'] * (1 + np.tanh(engagement_weight))
        }

        self.posts.append(result)
        return result

    def analyze_reddit_post(self, title, content, upvote_ratio=None,
                          num_comments=None, timestamp=None):
        """
        Analyze sentiment from a Reddit post.

        Parameters:
        title: Post title
        content: Post content
        upvote_ratio: Upvote ratio (0-1)
        num_comments: Number of comments
        timestamp: Post timestamp

        Returns:
        dict with sentiment and community engagement score
        """
        full_text = f"{title} {content}" if content else title
        sentiment = self.vader_analyzer.analyze_text(full_text)

        # Upvote ratio as credibility indicator
        if upvote_ratio is None:
            upvote_ratio = 0.5

        credibility_weight = abs(upvote_ratio - 0.5) * 2  # 0-1 range

        # Comments as engagement indicator
        comment_weight = np.log1p(num_comments) if num_comments else 0

        result = {
            'timestamp': timestamp or datetime.now(),
            'title': title,
            'sentiment_score': sentiment['compound'],
            'positive': sentiment['positive'],
            'negative': sentiment['negative'],
            'neutral': sentiment['neutral'],
            'upvote_ratio': upvote_ratio,
            'num_comments': num_comments or 0,
            'credibility_weight': credibility_weight,
            'comment_weight': comment_weight,
            'weighted_sentiment': sentiment['compound'] * (1 + credibility_weight + 0.1 * comment_weight)
        }

        self.posts.append(result)
        return result

    def aggregate_sentiment(self, lookback_hours=24, min_engagement=1):
        """
        Aggregate social media sentiment.

        Parameters:
        lookback_hours: Hours to look back
        min_engagement: Minimum engagement weight

        Returns:
        dict with aggregate metrics
        """
        if not self.posts:
            return {
                'avg_sentiment': 0.0,
                'weighted_avg_sentiment': 0.0,
                'sentiment_std': 0.0,
                'bullish_posts': 0,
                'bearish_posts': 0,
                'post_count': 0,
                'total_engagement': 0.0
            }

        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        recent = [p for p in self.posts if p['timestamp'] >= cutoff_time]

        if not recent:
            return {
                'avg_sentiment': 0.0,
                'weighted_avg_sentiment': 0.0,
                'sentiment_std': 0.0,
                'bullish_posts': 0,
                'bearish_posts': 0,
                'post_count': 0,
                'total_engagement': 0.0
            }

        sentiments = [p['sentiment_score'] for p in recent]
        weighted_sentiments = [p['weighted_sentiment'] for p in recent]
        engagements = [p.get('engagement_weight', p.get('comment_weight', 0)) for p in recent]

        bullish = sum(1 for s in sentiments if s > 0.05)
        bearish = sum(1 for s in sentiments if s < -0.05)

        return {
            'avg_sentiment': np.mean(sentiments),
            'weighted_avg_sentiment': np.mean(weighted_sentiments),
            'sentiment_std': np.std(sentiments),
            'bullish_posts': bullish,
            'bearish_posts': bearish,
            'post_count': len(sentiments),
            'total_engagement': np.sum(engagements),
            'avg_engagement': np.mean(engagements) if engagements else 0.0,
            'bullish_ratio': bullish / len(sentiments) if sentiments else 0
        }


class SentimentSignalGenerator:
    """Generate trading signals from sentiment analysis."""

    def __init__(self, news_threshold=0.1, social_threshold=0.15,
                 momentum_weight=0.3):
        self.news_threshold = news_threshold
        self.social_threshold = social_threshold
        self.momentum_weight = momentum_weight
        self.signal_history = []

    def generate_signal(self, news_sentiment, social_sentiment,
                       price_momentum=0, volume_signal=0):
        """
        Generate trading signal from sentiment and technical indicators.

        Parameters:
        news_sentiment: News sentiment aggregation dict
        social_sentiment: Social media sentiment aggregation dict
        price_momentum: Price momentum signal (-1 to 1)
        volume_signal: Volume signal (-1 to 1)

        Returns:
        dict with signal strength and recommendation
        """
        # Extract sentiment scores
        news_score = news_sentiment.get('avg_sentiment', 0)
        social_score = social_sentiment.get('weighted_avg_sentiment', 0)
        news_momentum = news_sentiment.get('sentiment_momentum', 0)

        # Weighted combination
        combined_sentiment = 0.5 * news_score + 0.5 * social_score

        # Incorporate momentum
        signal_strength = (
            combined_sentiment +
            self.momentum_weight * news_momentum +
            0.2 * price_momentum +
            0.1 * volume_signal
        )

        # Normalize signal strength
        signal_strength = np.clip(signal_strength, -1, 1)

        # Generate recommendation
        if signal_strength > self.news_threshold:
            recommendation = 'BUY'
            confidence = min(1.0, signal_strength)
        elif signal_strength < -self.news_threshold:
            recommendation = 'SELL'
            confidence = min(1.0, abs(signal_strength))
        else:
            recommendation = 'HOLD'
            confidence = 1.0 - abs(signal_strength)

        result = {
            'timestamp': datetime.now(),
            'news_score': news_score,
            'social_score': social_score,
            'combined_sentiment': combined_sentiment,
            'news_momentum': news_momentum,
            'signal_strength': signal_strength,
            'recommendation': recommendation,
            'confidence': confidence,
            'buy_pressure': max(0, signal_strength),
            'sell_pressure': max(0, -signal_strength)
        }

        self.signal_history.append(result)
        return result

    def get_signal_statistics(self, window=20):
        """
        Get statistics on generated signals.

        Parameters:
        window: Number of recent signals to analyze

        Returns:
        dict with signal statistics
        """
        if len(self.signal_history) < window:
            recent_signals = self.signal_history
        else:
            recent_signals = self.signal_history[-window:]

        if not recent_signals:
            return {
                'avg_signal_strength': 0.0,
                'buy_count': 0,
                'sell_count': 0,
                'hold_count': 0,
                'win_rate': 0.0
            }

        recommendations = [s['recommendation'] for s in recent_signals]
        signal_strengths = [s['signal_strength'] for s in recent_signals]

        return {
            'avg_signal_strength': np.mean(signal_strengths),
            'signal_std': np.std(signal_strengths),
            'buy_count': sum(1 for r in recommendations if r == 'BUY'),
            'sell_count': sum(1 for r in recommendations if r == 'SELL'),
            'hold_count': sum(1 for r in recommendations if r == 'HOLD'),
            'bullish_ratio': sum(1 for r in recommendations if r == 'BUY') / len(recommendations)
        }


class AggregateSentimentIndex:
    """Create aggregate sentiment indices combining multiple sources."""

    def __init__(self):
        self.news_scorer = NewsSentimentScorer()
        self.social_analyzer = SocialMediaSentimentAnalyzer()
        self.signal_generator = SentimentSignalGenerator()
        self.index_history = []

    def compute_sentiment_index(self, symbol, lookback_hours=24):
        """
        Compute comprehensive sentiment index for a security.

        Parameters:
        symbol: Security symbol
        lookback_hours: Hours to look back

        Returns:
        dict with multi-source sentiment index
        """
        # Aggregate news sentiment
        news_agg = self.news_scorer.aggregate_sentiment(lookback_hours)

        # Aggregate social media sentiment
        social_agg = self.social_analyzer.aggregate_sentiment(lookback_hours)

        # Calculate overall index (0-100 scale)
        news_index = 50 + (news_agg.get('avg_sentiment', 0) * 50)
        social_index = 50 + (social_agg.get('weighted_avg_sentiment', 0) * 50)

        # Weighted overall index
        overall_index = (
            0.4 * news_index +
            0.3 * social_index +
            0.2 * (50 + news_agg.get('sentiment_momentum', 0) * 50) +
            0.1 * (50 + max(-1, min(1, social_agg.get('bullish_ratio', 0.5) - 0.5)) * 100)
        )

        index_data = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'news_index': np.clip(news_index, 0, 100),
            'social_index': np.clip(social_index, 0, 100),
            'momentum_index': np.clip(50 + news_agg.get('sentiment_momentum', 0) * 50, 0, 100),
            'engagement_index': np.clip(50 + np.tanh(social_agg.get('avg_engagement', 0)) * 50, 0, 100),
            'overall_index': np.clip(overall_index, 0, 100),
            'articles_count': news_agg.get('total_articles', 0),
            'posts_count': social_agg.get('post_count', 0),
            'news_sentiment': news_agg.get('avg_sentiment', 0),
            'social_sentiment': social_agg.get('weighted_avg_sentiment', 0),
            'positive_ratio': news_agg.get('positive_ratio', 0)
        }

        self.index_history.append(index_data)
        return index_data

    def get_index_signals(self, lookback_periods=5):
        """
        Generate signals based on index levels and trends.

        Parameters:
        lookback_periods: Number of periods to analyze

        Returns:
        dict with index-based signals
        """
        if len(self.index_history) < lookback_periods:
            recent_indices = self.index_history
        else:
            recent_indices = self.index_history[-lookback_periods:]

        if not recent_indices:
            return {
                'index_trend': 0.0,
                'extremes_detected': False,
                'signal': 'HOLD'
            }

        indices = [idx['overall_index'] for idx in recent_indices]

        # Calculate trend
        if len(indices) > 1:
            trend = (indices[-1] - indices[0]) / (len(indices) - 1)
        else:
            trend = 0.0

        current_index = indices[-1]
        extreme = current_index > 70 or current_index < 30

        # Generate signal
        if current_index > 65 and trend > 0:
            signal = 'STRONG_BUY'
        elif current_index > 60:
            signal = 'BUY'
        elif current_index < 35 and trend < 0:
            signal = 'STRONG_SELL'
        elif current_index < 40:
            signal = 'SELL'
        else:
            signal = 'HOLD'

        return {
            'current_index': current_index,
            'index_trend': trend,
            'extremes_detected': extreme,
            'signal': signal,
            'index_std': np.std(indices) if indices else 0.0
        }

    def export_to_dataframe(self):
        """
        Export index history to DataFrame.

        Returns:
        DataFrame with sentiment index history
        """
        if not self.index_history:
            return pd.DataFrame()

        return pd.DataFrame(self.index_history)


# Convenience function for batch analysis
def analyze_texts_batch(texts, use_vader=True, use_finbert=False):
    """
    Batch analyze multiple texts.

    Parameters:
    texts: List of text strings
    use_vader: Use VADER analysis
    use_finbert: Use FinBERT analysis

    Returns:
    DataFrame with sentiment scores
    """
    results = []

    if use_vader:
        vader = VADERSentimentAnalyzer()
        for text in texts:
            scores = vader.analyze_text(text)
            scores['text'] = text
            results.append(scores)

    df = pd.DataFrame(results)
    return df
