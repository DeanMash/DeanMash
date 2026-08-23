import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_closeloop_web.db"
os.environ["SEED_DEMO"] = "true"
os.environ["SECRET_KEY"] = "test-secret"

Path("test_closeloop_web.db").unlink(missing_ok=True)

from closeloop.config import get_settings
from closeloop.db import init_db

get_settings.cache_clear()
init_db(get_settings().database_url)

from fastapi.testclient import TestClient

from closeloop.web import app


def test_landing_register_guide_advertise():
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert "Register your company" in r.text
        assert "WhatsApp" in r.text

        guide = client.get("/guide")
        assert guide.status_code == 200
        assert "Step-by-step" in guide.text

        ads = client.get("/advertise")
        assert ads.status_code == 200
        assert "Catalogue" in ads.text or "catalogue" in ads.text
        assert "/register" in ads.text

        assert client.get("/api/health").json()["ok"] is True


def test_public_register_add_client_and_followups():
    with TestClient(app) as client:
        assert client.get("/dashboard", follow_redirects=False).status_code == 303

        registered = client.post(
            "/register",
            data={
                "name": "Bright Coat Painting",
                "owner_name": "Alex Rivera",
                "phone": "5550100",
                "email": "alex@brightcoat.test",
                "password": "secret12",
                "trade_key": "painting",
                "plan_key": "starter",
            },
            follow_redirects=False,
        )
        assert registered.status_code == 303
        assert "/estimates/new" in registered.headers["location"]

        form = client.get("/estimates/new")
        assert form.status_code == 200
        assert "WhatsApp" in form.text

        created = client.post(
            "/estimates",
            data={
                "homeowner_name": "Taylor Client",
                "homeowner_phone": "+15550998877",
                "homeowner_email": "taylor@example.com",
                "address": "100 Test Rd",
                "job_title": "Interior repaint",
                "amount": "2800",
                "trade_key": "painting",
                "quoted_on": "2026-01-01",
                "notes": "",
            },
            follow_redirects=False,
        )
        assert created.status_code == 303

        dash = client.get("/dashboard")
        assert dash.status_code == 200
        assert "Taylor Client" in dash.text
        assert "Bright Coat Painting" in dash.text

        ran = client.post("/run-followups", follow_redirects=False)
        assert ran.status_code == 303


def test_demo_login():
    with TestClient(app) as client:
        bad = client.post(
            "/login",
            data={"email": "demo@closeloop.local", "password": "wrong"},
            follow_redirects=False,
        )
        assert bad.status_code == 400

        ok = client.post(
            "/login",
            data={"email": "demo@closeloop.local", "password": "demo1234"},
            follow_redirects=False,
        )
        assert ok.status_code == 303
        assert client.get("/dashboard").status_code == 200