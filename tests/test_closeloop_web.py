import os

# Use a file DB for web tests so lifespan seed + TestClient share state.
os.environ["DATABASE_URL"] = "sqlite:///./test_closeloop_web.db"
os.environ["SEED_DEMO"] = "true"

from closeloop.config import get_settings
from closeloop.db import init_db

get_settings.cache_clear()
init_db(get_settings().database_url)

from fastapi.testclient import TestClient

from closeloop.web import app

client = TestClient(app)


def test_landing_and_health():
    r = client.get("/")
    assert r.status_code == 200
    assert "Day 2" in r.text
    assert "$500" in r.text and "$1,500" in r.text
    assert client.get("/api/health").json()["ok"] is True


def test_dashboard_seeded_and_create_estimate():
    dash = client.get("/dashboard")
    assert dash.status_code == 200
    assert "Open pipeline" in dash.text

    form = client.get("/estimates/new")
    assert form.status_code == 200

    created = client.post(
        "/estimates",
        data={
            "homeowner_name": "Test Owner",
            "homeowner_phone": "+15550998877",
            "homeowner_email": "test@example.com",
            "address": "100 Test Rd",
            "job_title": "Demo job",
            "amount": "1234",
            "trade_key": "roofing",
            "quoted_on": "2026-01-01",
            "notes": "",
        },
        follow_redirects=False,
    )
    assert created.status_code == 303

    dash2 = client.get("/dashboard")
    assert "Test Owner" in dash2.text

    ran = client.post("/run-followups", follow_redirects=False)
    assert ran.status_code == 303