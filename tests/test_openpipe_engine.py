from datetime import datetime, timedelta, timezone
from pathlib import Path

from openpipe.engine import OutreachEngine
from openpipe.messaging import MessageSender
from openpipe.prospects import discover
from openpipe.store import Store
from openpipe.templates_msg import render_sequence


def test_render_sequence_personalizes():
    copy = render_sequence(
        "insurance",
        0,
        prospect_name="Tendai Chirwa",
        company="BrightPath Logistics",
        title="Managing Director",
        trigger="Just added 8 delivery vans",
        sender_name="Tariro Moyo",
        business_name="Horizon Cover Brokers",
    )
    assert "Tendai" in copy.body
    assert "BrightPath" in copy.body
    assert "Tariro" in copy.body
    assert "vans" in copy.body.lower() or "8 delivery" in copy.body


def test_discover_filters_by_vertical_and_city():
    hits = discover(vertical="insurance", city="Harare", niche="fleet", limit=5)
    assert hits
    assert any("fleet" in p.niche_tags or "insurance" in p.niche_tags for p in hits)


def test_plan_and_run_due(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    biz = store.create_business(
        name="Test Brokers",
        vertical="insurance",
        city="Harare",
        sender_name="Tariro",
        sender_email="tariro@test.example",
        booking_link="https://cal.example/test",
        offer="a cover gap review",
        plan="starter",
        niche="fleet",
    )
    prospect = store.add_prospect(
        biz.id,
        full_name="Farai Dube",
        email="farai@steelcity.example",
        title="Ops Director",
        company="Steel City",
        trigger="Won a municipal tender",
    )
    engine = OutreachEngine(store, MessageSender(mode="demo"))
    planned = engine.plan_prospect(biz.id, prospect)
    assert len(planned) == 3
    assert {m.day for m in planned} == {0, 3, 7}

    for msg in store.list_messages(biz.id):
        store.upsert_message(
            type(msg)(
                **{
                    **msg.__dict__,
                    "scheduled_for": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                    "status": "queued",
                }
            )
        )

    result = engine.run_due(biz.id)
    assert result["sent"] >= 1
    assert store.stats(biz.id)["messages_sent"] >= 1


def test_replied_skips_remaining(tmp_path: Path):
    store = Store(tmp_path / "reply.db")
    biz = store.seed_demo(force=True)
    engine = OutreachEngine(store, MessageSender(mode="demo"))
    engine.plan_business(biz.id)
    prospect = next(p for p in store.list_prospects(biz.id) if p.status == "sequenced")
    engine.mark_replied(prospect.id)
    refreshed = store.get_prospect(prospect.id)
    assert refreshed is not None
    assert refreshed.status == "replied"
    queued = [
        m
        for m in store.list_messages(biz.id)
        if m.prospect_id == prospect.id and m.status == "queued"
    ]
    assert queued == []
