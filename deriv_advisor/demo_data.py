from __future__ import annotations

from datetime import datetime, timezone

from .analyzer import InstagramSignal, NewsSentiment, TechnicalSignal
from .config import Config
from .deriv_client import AccountInfo
from .instagram_client import InstagramPost
from .markets import DEFAULT_SYMBOLS, normalize_symbols
from .service import AdviceReport
from .suggester import TradeSuggestion


_DEMO_TECHNICALS: dict[str, TechnicalSignal] = {
    "R_10": TechnicalSignal("R_10", "PUT", 58.0, ["Fast SMA below slow SMA"], 6200.8, 66.0, -0.09),
    "R_25": TechnicalSignal("R_25", "HOLD", 40.0, ["Flat momentum"], 4501.2, 51.0, 0.01),
    "R_50": TechnicalSignal("R_50", "PUT", 61.0, ["RSI overbought"], 210.4, 71.0, -0.12),
    "R_75": TechnicalSignal("R_75", "CALL", 74.0, ["Positive short-term momentum"], 89012.3, 38.0, 0.31),
    "R_100": TechnicalSignal("R_100", "CALL", 68.0, ["Fast SMA above slow SMA"], 1234.56, 42.0, 0.18),
    "1HZ75V": TechnicalSignal("1HZ75V", "CALL", 66.0, ["Positive short-term momentum"], 81234.1, 44.0, 0.22),
    "1HZ100V": TechnicalSignal("1HZ100V", "PUT", 59.0, ["Fast SMA below slow SMA"], 9912.4, 63.0, -0.08),
    "BOOM1000": TechnicalSignal("BOOM1000", "CALL", 71.0, ["Positive short-term momentum"], 11234.5, 39.0, 0.27),
    "CRASH1000": TechnicalSignal("CRASH1000", "PUT", 69.0, ["Negative short-term momentum"], 8876.2, 68.0, -0.21),
    "JD10": TechnicalSignal("JD10", "HOLD", 42.0, ["Flat momentum"], 1502.3, 50.0, 0.02),
    "JD25": TechnicalSignal("JD25", "CALL", 63.0, ["Fast SMA above slow SMA"], 3201.8, 41.0, 0.14),
    "JD50": TechnicalSignal("JD50", "PUT", 60.0, ["RSI overbought"], 5400.1, 70.0, -0.11),
    "JD75": TechnicalSignal("JD75", "CALL", 65.0, ["Positive short-term momentum"], 7100.4, 43.0, 0.16),
    "JD100": TechnicalSignal("JD100", "HOLD", 45.0, ["RSI neutral"], 9800.9, 52.0, 0.03),
}


def demo_config() -> Config:
    return Config(
        app_id="1089",
        api_token="demo",
        symbols=list(DEFAULT_SYMBOLS),
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


def build_demo_report(
    *,
    instagram_urls: list[str] | None = None,
    symbols: list[str] | None = None,
) -> AdviceReport:
    urls = instagram_urls or []
    watchlist = normalize_symbols(symbols) if symbols else list(DEFAULT_SYMBOLS)
    if not watchlist:
        watchlist = list(DEFAULT_SYMBOLS)

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

    technicals: list[TechnicalSignal] = []
    for symbol in watchlist:
        if symbol in _DEMO_TECHNICALS:
            technicals.append(_DEMO_TECHNICALS[symbol])
        else:
            technicals.append(
                TechnicalSignal(
                    symbol=symbol,
                    direction="HOLD",
                    confidence=45.0,
                    reasons=["Demo placeholder for this index"],
                    last_price=1000.0,
                    rsi=50.0,
                    momentum_pct=0.0,
                )
            )

    suggestions = [
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
            symbol="BOOM1000",
            direction="CALL",
            confidence=71.0,
            last_price=11234.5,
            reasons=[
                "Positive short-term momentum (+0.270%)",
                "News: News tone is mixed/neutral. (score +0.12)",
                "Instagram: no links provided.",
                "No recent personal trades found.",
            ],
            news_adjustment=0.7,
            instagram_adjustment=0.0,
            trade_history_note="No recent personal trades found.",
        ),
        TradeSuggestion(
            symbol="CRASH1000",
            direction="PUT",
            confidence=69.0,
            last_price=8876.2,
            reasons=[
                "Negative short-term momentum (-0.210%)",
                "News: News tone is mixed/neutral. (score +0.12)",
                "Instagram: no links provided.",
                "No recent personal trades found.",
            ],
            news_adjustment=-0.7,
            instagram_adjustment=0.0,
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
    ]
    watched = set(watchlist)
    suggestions = [s for s in suggestions if s.symbol in watched]

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
        technicals=technicals,
        trades=[],
        suggestions=suggestions,
        min_confidence=55,
        cache_hit=False,
        instagram=instagram,
        instagram_posts=posts,
    )
