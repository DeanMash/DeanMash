from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .analyzer import (
    InstagramSignal,
    NewsSentiment,
    TechnicalSignal,
    analyze_instagram,
    analyze_news,
    analyze_ticks,
)
from .cache import news_cache, report_cache, ticks_cache, trades_cache
from .config import Config
from .deriv_client import AccountInfo, DerivClient, StatementTrade, TickSeries
from .instagram_client import InstagramPost, extract_instagram_urls, fetch_instagram_posts
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
    cache_hit: bool = False
    instagram: InstagramSignal = field(
        default_factory=lambda: InstagramSignal(
            score=0.0,
            direction_hint="HOLD",
            matched_symbols=[],
            post_count=0,
            fetched_count=0,
            sample_captions=[],
            summary="No Instagram links provided.",
        )
    )
    instagram_posts: list[InstagramPost] = field(default_factory=list)

    def to_text(self, *, compact: bool = False) -> str:
        account_type = "DEMO" if self.account.is_virtual else "REAL"
        lines = [
            "Deriv Trade Advisor — SUGGESTIONS ONLY",
            "This tool never places trades.",
            f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            + (" (cache)" if self.cache_hit else ""),
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
        lines.append("Instagram")
        lines.append(f"• {self.instagram.summary}")
        for caption in self.instagram.sample_captions[: 2 if compact else 4]:
            lines.append(f"  - {caption}")

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

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "cache_hit": self.cache_hit,
            "min_confidence": self.min_confidence,
            "account": {
                "loginid": self.account.loginid,
                "currency": self.account.currency,
                "balance": self.account.balance,
                "is_virtual": self.account.is_virtual,
                "type": "DEMO" if self.account.is_virtual else "REAL",
            },
            "news": {
                "score": self.news.score,
                "headline_count": self.news.headline_count,
                "summary": self.news.summary,
                "sample_titles": self.news.sample_titles,
            },
            "instagram": {
                "score": self.instagram.score,
                "direction_hint": self.instagram.direction_hint,
                "matched_symbols": self.instagram.matched_symbols,
                "post_count": self.instagram.post_count,
                "fetched_count": self.instagram.fetched_count,
                "summary": self.instagram.summary,
                "sample_captions": self.instagram.sample_captions,
                "posts": [
                    {
                        "url": p.url,
                        "fetched": p.fetched,
                        "media_type": p.media_type,
                        "author": p.author,
                        "title": p.title,
                        "caption": p.caption[:240],
                        "note": p.note,
                    }
                    for p in self.instagram_posts
                ],
            },
            "suggestions": [
                {
                    "symbol": s.symbol,
                    "direction": s.direction,
                    "confidence": s.confidence,
                    "last_price": s.last_price,
                    "reasons": s.reasons,
                    "news_adjustment": s.news_adjustment,
                    "instagram_adjustment": s.instagram_adjustment,
                }
                for s in self.suggestions
            ],
            "technicals": [
                {
                    "symbol": t.symbol,
                    "direction": t.direction,
                    "confidence": t.confidence,
                    "last_price": t.last_price,
                    "rsi": t.rsi,
                    "momentum_pct": t.momentum_pct,
                }
                for t in self.technicals
            ],
        }


def _report_cache_key(config: Config, urls: list[str]) -> str:
    return "|".join(
        [
            "report",
            ",".join(config.symbols),
            str(config.tick_count),
            str(config.min_confidence),
            config.news_api_key or "-",
            ",".join(sorted(urls)),
        ]
    )


def _get_news_items(config: Config) -> list[NewsItem]:
    key = f"news|{config.news_api_key or '-'}"
    cached = news_cache.get(key)
    if cached is not None:
        logger.debug("News cache hit")
        return cached
    items = fetch_news(config.news_api_key, max_items=20)
    return news_cache.set(key, items, config.cache_ttl_seconds)


async def _get_ticks(
    client: DerivClient,
    config: Config,
    symbol: str,
) -> TickSeries:
    key = f"ticks|{symbol}|{config.tick_count}"
    cached = ticks_cache.get(key)
    if cached is not None:
        logger.debug("Ticks cache hit for %s", symbol)
        return cached
    series = await client.get_ticks_history(symbol, config.tick_count)
    return ticks_cache.set(key, series, config.cache_ttl_seconds)


async def _get_trades(client: DerivClient, config: Config) -> list[StatementTrade]:
    key = f"trades|{config.api_token[-6:] if config.api_token else '-'}"
    cached = trades_cache.get(key)
    if cached is not None:
        logger.debug("Trades cache hit")
        return cached
    trades = await client.get_recent_trades(limit=30)
    return trades_cache.set(key, trades, config.cache_ttl_seconds)


async def _analyze_symbol(
    client: DerivClient,
    config: Config,
    symbol: str,
) -> TechnicalSignal | None:
    try:
        series = await _get_ticks(client, config, symbol)
        signal = analyze_ticks(series)
        logger.info("Analyzed %s ticks for %s", len(series.prices), symbol)
        return signal
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to analyze %s: %s", symbol, exc)
        return None


async def generate_advice_report(
    config: Config,
    *,
    instagram_urls: list[str] | None = None,
    bypass_cache: bool = False,
) -> AdviceReport:
    urls = list(instagram_urls or [])
    for url in config.instagram_urls:
        if url not in urls:
            urls.append(url)

    cache_key = _report_cache_key(config, urls)
    if not bypass_cache:
        cached_report = report_cache.get(cache_key)
        if cached_report is not None:
            cached_report.cache_hit = True
            logger.info("Advice report cache hit")
            return cached_report

    news_items = _get_news_items(config)
    news_sentiment = analyze_news(news_items)

    # Instagram is fetched only when links exist — keeps normal runs fast.
    if urls:
        instagram_posts = await asyncio.to_thread(
            fetch_instagram_posts,
            urls,
            config.facebook_access_token,
        )
    else:
        instagram_posts = []
    instagram_signal = analyze_instagram(instagram_posts)

    async with DerivClient(config.ws_url, config.api_token) as client:
        if client.account is None:
            raise RuntimeError("Deriv account was not authorized")
        account = client.account
        trades = await _get_trades(client, config)

        results = await asyncio.gather(
            *[_analyze_symbol(client, config, symbol) for symbol in config.symbols]
        )
        technicals = [signal for signal in results if signal is not None]

    suggestions = build_suggestions(
        technicals=technicals,
        news=news_sentiment,
        trades=trades,
        min_confidence=config.min_confidence,
        instagram=instagram_signal,
    )

    report = AdviceReport(
        generated_at=datetime.now(timezone.utc),
        account=account,
        news=news_sentiment,
        news_items=news_items,
        technicals=technicals,
        trades=trades,
        suggestions=suggestions,
        min_confidence=config.min_confidence,
        cache_hit=False,
        instagram=instagram_signal,
        instagram_posts=instagram_posts,
    )
    report_cache.set(cache_key, report, config.cache_ttl_seconds)
    return report


def parse_instagram_input(text: str) -> list[str]:
    return extract_instagram_urls(text)
