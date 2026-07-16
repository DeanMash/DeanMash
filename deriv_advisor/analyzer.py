from __future__ import annotations

from dataclasses import dataclass

from .deriv_client import TickSeries
from .news_client import NewsItem


BULLISH_WORDS = {
    "surge",
    "rally",
    "gain",
    "gains",
    "rise",
    "rises",
    "rose",
    "bull",
    "bullish",
    "growth",
    "strong",
    "beat",
    "record",
    "optimistic",
    "recovery",
    "upbeat",
    "jump",
    "jumps",
}

BEARISH_WORDS = {
    "fall",
    "falls",
    "fell",
    "drop",
    "drops",
    "decline",
    "declines",
    "crash",
    "bear",
    "bearish",
    "weak",
    "loss",
    "losses",
    "recession",
    "fear",
    "cut",
    "cuts",
    "slump",
    "inflation",
    "war",
    "tariff",
}


@dataclass
class TechnicalSignal:
    symbol: str
    direction: str  # CALL / PUT / HOLD
    confidence: float
    reasons: list[str]
    last_price: float
    rsi: float
    momentum_pct: float


@dataclass
class NewsSentiment:
    score: float  # -1.0 (bearish) to +1.0 (bullish)
    headline_count: int
    sample_titles: list[str]
    summary: str


def _sma(values: list[float], window: int) -> float:
    if len(values) < window:
        return sum(values) / len(values)
    return sum(values[-window:]) / window


def _rsi(prices: list[float], period: int = 14) -> float:
    if len(prices) <= period:
        return 50.0

    gains = 0.0
    losses = 0.0
    for i in range(-period, 0):
        change = prices[i] - prices[i - 1]
        if change >= 0:
            gains += change
        else:
            losses -= change

    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def analyze_ticks(series: TickSeries) -> TechnicalSignal:
    prices = series.prices
    last = prices[-1]
    sma_fast = _sma(prices, 10)
    sma_slow = _sma(prices, 30)
    rsi = _rsi(prices, 14)
    lookback = min(20, len(prices) - 1)
    momentum_pct = ((last - prices[-lookback - 1]) / prices[-lookback - 1]) * 100

    bull_score = 0.0
    bear_score = 0.0
    reasons: list[str] = []

    if sma_fast > sma_slow:
        bull_score += 30
        reasons.append(f"Fast SMA ({sma_fast:.5f}) above slow SMA ({sma_slow:.5f})")
    elif sma_fast < sma_slow:
        bear_score += 30
        reasons.append(f"Fast SMA ({sma_fast:.5f}) below slow SMA ({sma_slow:.5f})")

    if rsi < 35:
        bull_score += 25
        reasons.append(f"RSI oversold ({rsi:.1f})")
    elif rsi > 65:
        bear_score += 25
        reasons.append(f"RSI overbought ({rsi:.1f})")
    else:
        reasons.append(f"RSI neutral ({rsi:.1f})")

    if momentum_pct > 0.05:
        bull_score += 25
        reasons.append(f"Positive short-term momentum ({momentum_pct:+.3f}%)")
    elif momentum_pct < -0.05:
        bear_score += 25
        reasons.append(f"Negative short-term momentum ({momentum_pct:+.3f}%)")
    else:
        reasons.append(f"Flat momentum ({momentum_pct:+.3f}%)")

    # Mild mean-reversion cue near extremes.
    if last < sma_slow * 0.998:
        bull_score += 10
        reasons.append("Price slightly below slow SMA (possible bounce)")
    elif last > sma_slow * 1.002:
        bear_score += 10
        reasons.append("Price slightly above slow SMA (possible pullback)")

    if bull_score == bear_score:
        direction = "HOLD"
        confidence = 40.0
    elif bull_score > bear_score:
        direction = "CALL"
        confidence = min(92.0, 45.0 + (bull_score - bear_score))
    else:
        direction = "PUT"
        confidence = min(92.0, 45.0 + (bear_score - bull_score))

    return TechnicalSignal(
        symbol=series.symbol,
        direction=direction,
        confidence=round(confidence, 1),
        reasons=reasons,
        last_price=last,
        rsi=round(rsi, 1),
        momentum_pct=round(momentum_pct, 4),
    )


def analyze_news(items: list[NewsItem]) -> NewsSentiment:
    if not items:
        return NewsSentiment(
            score=0.0,
            headline_count=0,
            sample_titles=[],
            summary="No news headlines available.",
        )

    score = 0.0
    for item in items:
        text = f"{item.title} {item.summary}".lower()
        words = set(text.replace(":", " ").replace(",", " ").split())
        bull = len(words & BULLISH_WORDS)
        bear = len(words & BEARISH_WORDS)
        score += bull - bear

    # Normalize roughly into [-1, 1]
    norm = max(-1.0, min(1.0, score / max(6.0, len(items) * 0.8)))
    if norm > 0.15:
        summary = "News tone leans bullish."
    elif norm < -0.15:
        summary = "News tone leans bearish."
    else:
        summary = "News tone is mixed/neutral."

    return NewsSentiment(
        score=round(norm, 3),
        headline_count=len(items),
        sample_titles=[i.title for i in items[:5]],
        summary=summary,
    )
