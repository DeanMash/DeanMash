from pathlib import Path

from fastapi.testclient import TestClient

from openpipe.store import Store
from openpipe.web import create_app


def test_landing_register_and_apis(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENPIPE_DB_PATH", str(tmp_path / "web.db"))
    monkeypatch.setenv("OPENPIPE_DASHBOARD_TOKEN", "")
    monkeypatch.setenv("OPENPIPE_AUTO_RUN", "0")
    store = Store(tmp_path / "web.db")
    app = create_app(store)
    client = TestClient(app)

    assert client.get("/").status_code == 200
    assert client.get("/dashboard").status_code == 200
    assert client.get("/register").status_code == 200
    health = client.get("/api/health").json()
    assert health["product"] == "OpenPipe"
    assert "whatsapp" in health["channels"]

    verticals = client.get("/api/verticals").json()
    assert any(v["key"] == "insurance" for v in verticals)
    assert any(v["key"] == "advisor" for v in verticals)
    assert any(v["key"] == "b2b" for v in verticals)

    plans = client.get("/api/plans").json()
    prices = {p["price_usd"] for p in plans}
    assert 900 in prices and 2500 in prices

    starters = client.get("/api/starters").json()
    assert {s["vertical"] for s in starters} >= {"insurance", "advisor", "b2b"}

    samples = client.get("/api/samples").json()
    assert len(samples) == 3
    assert all(len(s["days"]) == 3 for s in samples)
    assert all(s["days"][0].get("whatsapp") for s in samples)

    businesses = client.get("/api/businesses").json()
    assert len(businesses) >= 3
    verticals_present = {b["vertical"] for b in businesses}
    assert {"insurance", "advisor", "b2b"} <= verticals_present

    reg = client.post(
        "/api/register",
        json={
            "owner_name": "Tariro",
            "business_name": "Tariro Cover",
            "vertical": "insurance",
            "email": "tariro@newfirm.example",
            "phone": "+263771112233",
            "city": "Harare",
            "niche": "fleet",
            "channels": "both",
            "plan": "starter",
            "seed_prospects": True,
        },
    )
    assert reg.status_code == 200, reg.text
    payload = reg.json()
    assert payload["status"] == "registered"
    token = payload["access_token"]
    biz_id = payload["business"]["id"]
    assert payload["seeded"]["added"] >= 1

    me = client.get(
        f"/api/business?business_id={biz_id}",
        headers={"X-Openpipe-Token": token},
    )
    assert me.status_code == 200
    assert me.json()["channels"] == "both"

    preview = client.get(
        f"/api/preview?business_id={biz_id}&prospect_id={store.list_prospects(biz_id)[0].id}&channel=whatsapp",
        headers={"X-Openpipe-Token": token},
    )
    assert preview.status_code == 200
    assert preview.json()["channel"] == "whatsapp"

    run = client.post(
        f"/api/run?business_id={biz_id}",
        headers={"X-Openpipe-Token": token},
        json={},
    )
    assert run.status_code == 200
    assert "by_channel" in run.json()

    login = client.post("/api/login", json={"access_token": token})
    assert login.status_code == 200
    assert login.json()["business"]["id"] == biz_id

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
