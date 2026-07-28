from fastapi.testclient import TestClient

from deriv_advisor.web import create_app


def test_demo_mode_suggestions():
    app = create_app(demo_mode=True)
    client = TestClient(app)
    health = client.get("/api/health").json()
    assert health["mode"] == "demo"
    response = client.post("/api/suggestions", json={"instagram_text": ""})
    assert response.status_code == 200
    payload = response.json()
    assert payload["account"]["loginid"] == "VRTC-DEMO"
    assert payload["suggestions"]
    assert payload["markets"]
    assert any(m["display_name"] for m in payload["markets"])
    assert payload["suggestions"][0]["symbol"] in {
        "R_75",
        "R_100",
        "R_50",
        "BOOM1000",
        "CRASH1000",
    }


def test_demo_mode_respects_selected_symbols():
    app = create_app(demo_mode=True)
    client = TestClient(app)
    response = client.post(
        "/api/suggestions",
        json={"symbols_text": "R_75, BOOM1000"},
    )
    assert response.status_code == 200
    payload = response.json()
    market_symbols = {m["symbol"] for m in payload["markets"]}
    assert market_symbols == {"R_75", "BOOM1000"}
    assert all(m["display_name"] for m in payload["markets"])
