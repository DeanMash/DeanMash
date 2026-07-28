from __future__ import annotations

from dataclasses import dataclass

from .analyzer import InstagramSignal, NewsSentiment, TechnicalSignal
from .deriv_client import StatementTrade


@dataclass
class TradeSuggestion:
    symbol: str
    direction: str
    confidence: float
    last_price: float
    reasons: list[str]
    news_adjustment: float
    instagram_adjustment: float
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


def _instagram_nudge(signal: TechnicalSignal, instagram: InstagramSignal) -> tuple[float, str]:
    if instagram.post_count == 0:
        return 0.0, "Instagram: no links provided."
    if instagram.fetched_count == 0:
        return 0.0, f"Instagram: {instagram.summary}"

    # Base nudge from caption tone.
    nudge = instagram.score * 8.0

    # Extra weight when the caption names this symbol.
    if instagram.matched_symbols and signal.symbol in instagram.matched_symbols:
        if instagram.direction_hint == signal.direction:
            nudge += 4.0
        elif instagram.direction_hint in {"CALL", "PUT"} and instagram.direction_hint != signal.direction:
            nudge -= 4.0

    # Align / conflict with technical direction.
    if instagram.direction_hint == signal.direction:
        applied = abs(nudge)
    elif instagram.direction_hint == "HOLD":
        applied = nudge * 0.35
    else:
        applied = -abs(nudge)

    note = f"Instagram: {instagram.summary} (adj {applied:+.1f})"
    return applied, note


def build_suggestions(
    technicals: list[TechnicalSignal],
    news: NewsSentiment,
    trades: list[StatementTrade],
    min_confidence: float,
    instagram: InstagramSignal | None = None,
) -> list[TradeSuggestion]:
    suggestions: list[TradeSuggestion] = []
    instagram = instagram or InstagramSignal(
        score=0.0,
        direction_hint="HOLD",
        matched_symbols=[],
        post_count=0,
        fetched_count=0,
        sample_captions=[],
        summary="No Instagram links provided.",
    )

    # News is more relevant for FX/commodities than pure synthetics, so keep the nudge small.
    news_nudge = news.score * 6.0

    for signal in technicals:
        if signal.direction == "HOLD":
            continue

        hist_nudge, hist_note = _trade_history_bias(trades, signal.symbol)
        ig_nudge, ig_note = _instagram_nudge(signal, instagram)
        adjusted = signal.confidence

        if signal.direction == "CALL":
            adjusted += news_nudge
        else:
            adjusted -= news_nudge

        adjusted += hist_nudge
        adjusted += ig_nudge
        adjusted = max(0.0, min(95.0, adjusted))

        reasons = list(signal.reasons)
        reasons.append(f"News: {news.summary} (score {news.score:+.2f})")
        reasons.append(ig_note)
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
                instagram_adjustment=round(ig_nudge, 2),
                trade_history_note=hist_note,
            )
        )

    suggestions.sort(key=lambda s: s.confidence, reverse=True)
    return suggestions
