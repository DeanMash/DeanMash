from pathlib import Path

from fastapi.testclient import TestClient

from openpipe.store import Store
from openpipe.web import create_app


def test_landing_and_apis(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENPIPE_DB_PATH", str(tmp_path / "web.db"))
    monkeypatch.setenv("OPENPIPE_DASHBOARD_TOKEN", "")
    store = Store(tmp_path / "web.db")
    app = create_app(store)
    client = TestClient(app)

    assert client.get("/").status_code == 200
    assert client.get("/dashboard").status_code == 200
    assert client.get("/api/health").json()["product"] == "OpenPipe"

    verticals = client.get("/api/verticals").json()
    assert any(v["key"] == "insurance" for v in verticals)
    assert any(v["key"] == "advisor" for v in verticals)
    assert any(v["key"] == "b2b" for v in verticals)
    assert len(verticals) >= 8

    plans = client.get("/api/plans").json()
    prices = {p["price_usd"] for p in plans}
    assert 900 in prices and 2500 in prices

    stats = client.get("/api/stats").json()
    assert stats["prospects"] >= 1

    discover = client.post("/api/discover", json={"limit": 3})
    assert discover.status_code == 200
    assert "added" in discover.json()

    lead = client.post(
        "/api/leads",
        json={
            "name": "Dean",
            "business": "Horizon Cover",
            "vertical": "insurance",
            "email": "dean@example.com",
            "city": "Harare",
            "plan": "pipeline",
        },
    )
    assert lead.status_code == 200
    assert lead.json()["status"] == "received"
