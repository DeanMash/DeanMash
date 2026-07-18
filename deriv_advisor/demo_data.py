from __future__ import annotations

from datetime import datetime, timezone

from .analyzer import InstagramSignal, NewsSentiment, TechnicalSignal
from .config import Config
from .deriv_client import AccountInfo
from .instagram_client import InstagramPost
from .service import AdviceReport
from .suggester import TradeSuggestion


def demo_config() -> Config:
    return Config(
        app_id="1089",
        api_token="demo",
        symbols=["R_100", "R_75", "R_50", "R_25", "R_10"],
        tick_count=200,
        min_confidence=55,
        news_api_key=None,
        ws_url="wss://ws.derivws.com/websockets/v3?app_id=1089",
        telegram_bot_token=None,
        telegram_allowed_chat_ids=set(),
        dashboard_host="0.0.0.0",
        dashboard_port=8000,
        dashboard_token=None,
        facebook_access_token=None,
        instagram_urls=[],
        cache_ttl_seconds=45,
        alert_enabled=False,
        alert_interval_minutes=15,
        alert_min_confidence=70,
        alert_cooldown_minutes=30,
    )


def build_demo_report(*, instagram_urls: list[str] | None = None) -> AdviceReport:
    urls = instagram_urls or []
    has_ig = bool(urls)
    instagram = InstagramSignal(
        score=0.45 if has_ig else 0.0,
        direction_hint="CALL" if has_ig else "HOLD",
        matched_symbols=["R_75"] if has_ig else [],
        post_count=len(urls),
        fetched_count=1 if has_ig else 0,
        sample_captions=(
            ["Volatility 75 looking bullish — strong CALL breakout setup"] if has_ig else []
        ),
        summary=(
            "Instagram captions lean bullish/CALL. Mentioned: R_75."
            if has_ig
            else "No Instagram links provided."
        ),
    )
    posts = []
    if has_ig:
        posts = [
            InstagramPost(
                url=urls[0],
                caption="Volatility 75 looking bullish — strong CALL breakout setup",
                title="Demo trader on Instagram",
                author="demo_trader",
                media_type="reel",
                fetched=True,
                note="Demo caption (not a live Instagram fetch).",
            )
        ]

    return AdviceReport(
        generated_at=datetime.now(timezone.utc),
        account=AccountInfo(
            loginid="VRTC-DEMO",
            currency="USD",
            balance=10000.0,
            email=None,
            is_virtual=True,
        ),
        news=NewsSentiment(
            score=0.12,
            headline_count=4,
            sample_titles=[
                "Markets steady as traders await data",
                "Dollar softens after mixed economic prints",
                "Oil prices rise on supply concerns",
                "Tech shares extend weekly gains",
            ],
            summary="News tone is mixed/neutral.",
        ),
        news_items=[],
        technicals=[
            TechnicalSignal("R_100", "CALL", 68.0, ["Fast SMA above slow SMA"], 1234.56, 42.0, 0.18),
            TechnicalSignal("R_75", "CALL", 74.0, ["Positive short-term momentum"], 89012.3, 38.0, 0.31),
            TechnicalSignal("R_50", "PUT", 61.0, ["RSI overbought"], 210.4, 71.0, -0.12),
            TechnicalSignal("R_25", "HOLD", 40.0, ["Flat momentum"], 4501.2, 51.0, 0.01),
            TechnicalSignal("R_10", "PUT", 58.0, ["Fast SMA below slow SMA"], 6200.8, 66.0, -0.09),
        ],
        trades=[],
        suggestions=[
            TradeSuggestion(
                symbol="R_75",
                direction="CALL",
                confidence=78.5 if has_ig else 72.0,
                last_price=89012.3,
                reasons=[
                    "Positive short-term momentum (+0.310%)",
                    "Fast SMA above slow SMA",
                    "News: News tone is mixed/neutral. (score +0.12)",
                    (
                        "Instagram: Instagram captions lean bullish/CALL. Mentioned: R_75. (adj +4.0)"
                        if has_ig
                        else "Instagram: no links provided."
                    ),
                    "No recent personal trades found.",
                ],
                news_adjustment=0.7,
                instagram_adjustment=4.0 if has_ig else 0.0,
                trade_history_note="No recent personal trades found.",
            ),
            TradeSuggestion(
                symbol="R_100",
                direction="CALL",
                confidence=68.5,
                last_price=1234.56,
                reasons=[
                    "Fast SMA above slow SMA",
                    "RSI neutral (42.0)",
                    "News: News tone is mixed/neutral. (score +0.12)",
                    "Instagram: no links provided." if not has_ig else "Instagram: mild supportive tone.",
                    "No recent personal trades found.",
                ],
                news_adjustment=0.7,
                instagram_adjustment=0.5 if has_ig else 0.0,
                trade_history_note="No recent personal trades found.",
            ),
            TradeSuggestion(
                symbol="R_50",
                direction="PUT",
                confidence=61.0,
                last_price=210.4,
                reasons=[
                    "RSI overbought (71.0)",
                    "Negative short-term momentum (-0.120%)",
                    "News: News tone is mixed/neutral. (score +0.12)",
                    "Instagram: no links provided.",
                    "No recent personal trades found.",
                ],
                news_adjustment=-0.7,
                instagram_adjustment=0.0,
                trade_history_note="No recent personal trades found.",
            ),
        ],
        min_confidence=55,
        cache_hit=False,
        instagram=instagram,
        instagram_posts=posts,
    )
