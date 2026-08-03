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

    starters = client.get("/api/starters").json()
    assert {s["vertical"] for s in starters} >= {"insurance", "advisor", "b2b"}

    samples = client.get("/api/samples").json()
    assert len(samples) == 3
    assert all(len(s["days"]) == 3 for s in samples)

    businesses = client.get("/api/businesses").json()
    assert len(businesses) >= 3
    verticals_present = {b["vertical"] for b in businesses}
    assert {"insurance", "advisor", "b2b"} <= verticals_present

    advisor = next(b for b in businesses if b["vertical"] == "advisor")
    advisor_detail = client.get(f"/api/business?business_id={advisor['id']}").json()
    assert advisor_detail["vertical"] == "advisor"
    assert advisor_detail["start_tip"]

    insurance = next(b for b in businesses if b["vertical"] == "insurance")
    stats = client.get(f"/api/stats?business_id={insurance['id']}").json()
    assert stats["prospects"] >= 1

    b2b = next(b for b in businesses if b["vertical"] == "b2b")
    discover = client.post(f"/api/discover?business_id={b2b['id']}", json={"limit": 3})
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
