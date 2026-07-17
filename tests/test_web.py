from fastapi.testclient import TestClient

from deriv_advisor.config import Config
from deriv_advisor.web import create_app


def _config(*, token: str | None = "secret") -> Config:
    return Config(
        app_id="1089",
        api_token="dummy",
        symbols=["R_100"],
        tick_count=200,
        min_confidence=55,
        news_api_key=None,
        ws_url="wss://example.invalid",
        telegram_bot_token=None,
        telegram_allowed_chat_ids=set(),
        dashboard_host="127.0.0.1",
        dashboard_port=8000,
        dashboard_token=token,
        facebook_access_token=None,
        instagram_urls=[],
    )


def test_dashboard_index_and_health():
    app = create_app(_config())
    client = TestClient(app)
    assert client.get("/").status_code == 200
    health = client.get("/api/health").json()
    assert health["ok"] is True
    assert health["auth_required"] is True
    assert health["instagram_enabled"] is True


def test_suggestions_require_token(monkeypatch):
    async def fake_report(_config, **_kwargs):
        raise AssertionError("should not run without auth")

    monkeypatch.setattr("deriv_advisor.web.generate_advice_report", fake_report)
    app = create_app(_config(token="secret"))
    client = TestClient(app)
    denied = client.get("/api/suggestions")
    assert denied.status_code == 401


def test_suggestions_post_passes_instagram_urls(monkeypatch):
    captured = {}

    async def fake_report(config, *, instagram_urls=None):
        captured["urls"] = instagram_urls or []
        from datetime import datetime, timezone

        from deriv_advisor.analyzer import InstagramSignal, NewsSentiment
        from deriv_advisor.deriv_client import AccountInfo
        from deriv_advisor.service import AdviceReport

        return AdviceReport(
            generated_at=datetime.now(timezone.utc),
            account=AccountInfo("VRTC1", "USD", 100.0, None, True),
            news=NewsSentiment(0.0, 0, [], "No news"),
            news_items=[],
            technicals=[],
            trades=[],
            suggestions=[],
            min_confidence=55,
            instagram=InstagramSignal(0.0, "HOLD", [], 1, 0, [], "ok"),
        )

    monkeypatch.setattr("deriv_advisor.web.generate_advice_report", fake_report)
    app = create_app(_config(token=None))
    client = TestClient(app)
    response = client.post(
        "/api/suggestions",
        json={"instagram_text": "check https://www.instagram.com/reel/AbC123xyz/ now"},
    )
    assert response.status_code == 200
    assert captured["urls"] == ["https://www.instagram.com/reel/AbC123xyz/"]
