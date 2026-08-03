from pathlib import Path

from fastapi.testclient import TestClient

from comehome.store import Store
from comehome.web import create_app


def test_landing_and_apis(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("COMEHOME_DB_PATH", str(tmp_path / "web.db"))
    monkeypatch.setenv("COMEHOME_DASHBOARD_TOKEN", "")
    store = Store(tmp_path / "web.db")
    app = create_app(store)
    client = TestClient(app)

    assert client.get("/").status_code == 200
    assert client.get("/dashboard").status_code == 200
    assert client.get("/api/health").json()["product"] == "ComeHome"

    verticals = client.get("/api/verticals").json()
    assert any(v["key"] == "gym" for v in verticals)
    assert any(v["key"] == "salon" for v in verticals)
    assert len(verticals) >= 10

    plans = client.get("/api/plans").json()
    prices = {p["price_usd"] for p in plans}
    assert 800 in prices and 2000 in prices

    stats = client.get("/api/stats").json()
    assert stats["clients"] >= 1

    lead = client.post(
        "/api/leads",
        json={
            "name": "Dean",
            "business": "Avondale Physio",
            "vertical": "chiro",
            "phone": "+263771234567",
            "city": "Harare",
            "plan": "practice",
        },
    )
    assert lead.status_code == 200
    assert lead.json()["status"] == "received"
