from __future__ import annotations

from dataclasses import dataclass

from .analyzer import NewsSentiment, TechnicalSignal
from .deriv_client import StatementTrade


@dataclass
class TradeSuggestion:
    symbol: str
    direction: str
    confidence: float
    last_price: float
    reasons: list[str]
    news_adjustment: float
    trade_history_note: str


def _trade_history_bias(trades: list[StatementTrade], symbol: str) -> tuple[float, str]:
    """Small confidence nudge from recent personal trade outcomes on similar names."""
    if not trades:
        return 0.0, "No recent personal trades found."

    related = [
        t
        for t in trades
        if (t.symbol and symbol in str(t.symbol))
        or symbol.lower() in t.longcode.lower()
        or symbol.replace("_", "").lower() in t.longcode.lower()
    ]
    sample = related or trades[:10]
    wins = sum(1 for t in sample if t.amount > 0 and t.action_type == "sell")
    losses = sum(1 for t in sample if t.amount < 0 and t.action_type == "sell")
    settled = wins + losses
    if settled == 0:
        return 0.0, f"Recent activity: {len(sample)} transactions (no settled P/L yet)."

    win_rate = wins / settled
    if win_rate >= 0.6:
        return 3.0, f"Recent settled win rate {win_rate:.0%} ({wins}/{settled}) — mild confidence boost."
    if win_rate <= 0.4:
        return -4.0, f"Recent settled win rate {win_rate:.0%} ({wins}/{settled}) — mild confidence penalty."
    return 0.0, f"Recent settled win rate {win_rate:.0%} ({wins}/{settled}) — no adjustment."


def build_suggestions(
    technicals: list[TechnicalSignal],
    news: NewsSentiment,
    trades: list[StatementTrade],
    min_confidence: float,
) -> list[TradeSuggestion]:
    suggestions: list[TradeSuggestion] = []

    # News is more relevant for FX/commodities than pure synthetics, so keep the nudge small.
    news_nudge = news.score * 6.0

    for signal in technicals:
        if signal.direction == "HOLD":
            continue

        hist_nudge, hist_note = _trade_history_bias(trades, signal.symbol)
        adjusted = signal.confidence

        if signal.direction == "CALL":
            adjusted += news_nudge
        else:
            adjusted -= news_nudge

        adjusted += hist_nudge
        adjusted = max(0.0, min(95.0, adjusted))

        reasons = list(signal.reasons)
        reasons.append(f"News: {news.summary} (score {news.score:+.2f})")
        reasons.append(hist_note)

        if adjusted < min_confidence:
            continue

        suggestions.append(
            TradeSuggestion(
                symbol=signal.symbol,
                direction=signal.direction,
                confidence=round(adjusted, 1),
                last_price=signal.last_price,
                reasons=reasons,
                news_adjustment=round(news_nudge if signal.direction == "CALL" else -news_nudge, 2),
                trade_history_note=hist_note,
            )
        )

    suggestions.sort(key=lambda s: s.confidence, reverse=True)
    return suggestions
