import asyncio

from deriv_advisor.analyzer import NewsSentiment, TechnicalSignal
from deriv_advisor.config import Config
from deriv_advisor.deriv_client import AccountInfo, TickSeries
from deriv_advisor import service


def _config() -> Config:
    return Config(
        app_id="1089",
        api_token="dummy-token",
        symbols=["R_100", "R_75"],
        tick_count=200,
        min_confidence=55,
        news_api_key=None,
        ws_url="wss://example.invalid",
        telegram_bot_token=None,
        telegram_allowed_chat_ids=set(),
        dashboard_host="127.0.0.1",
        dashboard_port=8000,
        dashboard_token=None,
        facebook_access_token=None,
        instagram_urls=[],
        cache_ttl_seconds=60,
        alert_enabled=True,
        alert_interval_minutes=15,
        alert_min_confidence=70,
        alert_cooldown_minutes=30,
    )


def test_generate_advice_report_uses_parallel_ticks_and_cache(monkeypatch):
    service.news_cache.clear()
    service.ticks_cache.clear()
    service.trades_cache.clear()
    service.report_cache.clear()

    calls = {"ticks": 0}

    class FakeClient:
        account = AccountInfo("VRTC1", "USD", 100.0, None, True)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get_ticks_history(self, symbol, count):
            calls["ticks"] += 1
            await asyncio.sleep(0)  # allow concurrency
            prices = [100 + i * 0.2 for i in range(80)]
            return TickSeries(symbol=symbol, prices=prices, epochs=list(range(80)))

        async def get_recent_trades(self, limit=30):
            return []

    monkeypatch.setattr(service, "DerivClient", lambda *args, **kwargs: FakeClient())
    monkeypatch.setattr(service, "fetch_news", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        service,
        "analyze_ticks",
        lambda series: TechnicalSignal(
            symbol=series.symbol,
            direction="CALL",
            confidence=70.0,
            reasons=["up"],
            last_price=series.prices[-1],
            rsi=40.0,
            momentum_pct=0.2,
        ),
    )
    monkeypatch.setattr(
        service,
        "analyze_news",
        lambda items: NewsSentiment(0.0, 0, [], "No news headlines available."),
    )

    cfg = _config()

    async def run():
        report1 = await service.generate_advice_report(cfg)
        assert report1.cache_hit is False
        assert calls["ticks"] == 2
        assert len(report1.technicals) == 2

        report2 = await service.generate_advice_report(cfg)
        assert report2.cache_hit is True
        # Second call should not refetch ticks because full report was cached.
        assert calls["ticks"] == 2

    asyncio.run(run())
