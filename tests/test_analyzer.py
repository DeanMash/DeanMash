from deriv_advisor.analyzer import analyze_news, analyze_ticks
from deriv_advisor.deriv_client import TickSeries
from deriv_advisor.news_client import NewsItem
from deriv_advisor.suggester import build_suggestions


def test_analyze_ticks_detects_uptrend():
    prices = [100 + i * 0.2 for i in range(80)]
    series = TickSeries(symbol="R_100", prices=prices, epochs=list(range(len(prices))))
    signal = analyze_ticks(series)
    assert signal.direction == "CALL"
    assert signal.confidence >= 55


def test_analyze_ticks_detects_downtrend():
    prices = [100 - i * 0.2 for i in range(80)]
    series = TickSeries(symbol="R_75", prices=prices, epochs=list(range(len(prices))))
    signal = analyze_ticks(series)
    assert signal.direction == "PUT"
    assert signal.confidence >= 55


def test_news_sentiment_bullish_keywords():
    items = [
        NewsItem("Markets surge on strong growth", "Bullish rally continues", "Test", ""),
        NewsItem("Stocks rise to record highs", "Optimistic investors", "Test", ""),
    ]
    sentiment = analyze_news(items)
    assert sentiment.score > 0


def test_build_suggestions_respects_min_confidence():
    prices = [100 + i * 0.15 for i in range(80)]
    series = TickSeries(symbol="R_50", prices=prices, epochs=list(range(len(prices))))
    technical = analyze_ticks(series)
    news = analyze_news([])
    suggestions = build_suggestions([technical], news, trades=[], min_confidence=99)
    assert suggestions == []
