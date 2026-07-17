from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from .analyzer import NewsSentiment, TechnicalSignal, analyze_news, analyze_ticks
from .config import Config
from .deriv_client import AccountInfo, DerivClient, StatementTrade
from .news_client import NewsItem, fetch_news
from .suggester import TradeSuggestion, build_suggestions

logger = logging.getLogger(__name__)


@dataclass
class AdviceReport:
    generated_at: datetime
    account: AccountInfo
    news: NewsSentiment
    news_items: list[NewsItem]
    technicals: list[TechnicalSignal]
    trades: list[StatementTrade]
    suggestions: list[TradeSuggestion]
    min_confidence: float

    def to_text(self, *, compact: bool = False) -> str:
        account_type = "DEMO" if self.account.is_virtual else "REAL"
        lines = [
            "Deriv Trade Advisor — SUGGESTIONS ONLY",
            "This tool never places trades.",
            f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "Account",
            f"• {self.account.loginid} ({account_type})",
            f"• Balance: {self.account.balance:.2f} {self.account.currency}",
            "",
            "News",
            f"• {self.news.summary}",
            f"• Headlines analyzed: {self.news.headline_count}",
        ]

        for title in self.news.sample_titles[: 3 if compact else 5]:
            lines.append(f"  - {title}")

        lines.append("")
        lines.append(f"Suggestions (min {self.min_confidence:g}%)")

        if not self.suggestions:
            lines.append("• No ideas met the confidence threshold right now.")
        else:
            for idx, suggestion in enumerate(self.suggestions, start=1):
                lines.append(
                    f"#{idx} {suggestion.symbol} → {suggestion.direction} "
                    f"| {suggestion.confidence:.1f}% | last {suggestion.last_price}"
                )
                reason_limit = 2 if compact else len(suggestion.reasons)
                for reason in suggestion.reasons[:reason_limit]:
                    lines.append(f"   - {reason}")

        lines.extend(
            [
                "",
                "Disclaimer: heuristic signals only — not financial advice.",
            ]
        )
        return "\n".join(lines)


async def generate_advice_report(config: Config) -> AdviceReport:
    news_items = fetch_news(config.news_api_key, max_items=20)
    news_sentiment = analyze_news(news_items)

    async with DerivClient(config.ws_url, config.api_token) as client:
        if client.account is None:
            raise RuntimeError("Deriv account was not authorized")
        account = client.account
        trades = await client.get_recent_trades(limit=30)

        technicals: list[TechnicalSignal] = []
        for symbol in config.symbols:
            try:
                series = await client.get_ticks_history(symbol, config.tick_count)
                technicals.append(analyze_ticks(series))
                logger.info("Fetched %s ticks for %s", len(series.prices), symbol)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to analyze %s: %s", symbol, exc)

    suggestions = build_suggestions(
        technicals=technicals,
        news=news_sentiment,
        trades=trades,
        min_confidence=config.min_confidence,
    )

    return AdviceReport(
        generated_at=datetime.now(timezone.utc),
        account=account,
        news=news_sentiment,
        news_items=news_items,
        technicals=technicals,
        trades=trades,
        suggestions=suggestions,
        min_confidence=config.min_confidence,
    )
