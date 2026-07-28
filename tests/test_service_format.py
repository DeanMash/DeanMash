from datetime import datetime, timezone

from deriv_advisor.analyzer import NewsSentiment, TechnicalSignal
from deriv_advisor.deriv_client import AccountInfo
from deriv_advisor.service import AdviceReport
from deriv_advisor.suggester import TradeSuggestion


def test_advice_report_to_text_includes_suggestion():
    report = AdviceReport(
        generated_at=datetime(2026, 7, 17, tzinfo=timezone.utc),
        account=AccountInfo(
            loginid="VRTC123",
            currency="USD",
            balance=1000.0,
            email=None,
            is_virtual=True,
        ),
        news=NewsSentiment(
            score=0.1,
            headline_count=2,
            sample_titles=["Markets steady"],
            summary="News tone is mixed/neutral.",
        ),
        news_items=[],
        technicals=[
            TechnicalSignal(
                symbol="R_100",
                direction="CALL",
                confidence=70.0,
                reasons=["Positive momentum"],
                last_price=1234.5,
                rsi=40.0,
                momentum_pct=0.2,
            )
        ],
        trades=[],
        suggestions=[
            TradeSuggestion(
                symbol="R_100",
                direction="CALL",
                confidence=72.5,
                last_price=1234.5,
                reasons=["Positive momentum", "News: mixed"],
                news_adjustment=0.5,
                instagram_adjustment=1.5,
                trade_history_note="No recent personal trades found.",
            )
        ],
        min_confidence=55,
    )

    text = report.to_text(compact=True)
    assert "SUGGESTIONS ONLY" in text
    assert "VRTC123" in text
    assert "R_100 → CALL" in text
    assert "72.5%" in text

    payload = report.to_dict()
    assert payload["account"]["loginid"] == "VRTC123"
    assert payload["suggestions"][0]["direction"] == "CALL"
    assert payload["suggestions"][0]["confidence"] == 72.5
