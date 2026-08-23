from datetime import datetime, timedelta, timezone
from pathlib import Path

from openpipe.engine import OutreachEngine
from openpipe.messaging import MessageSender
from openpipe.prospects import discover
from openpipe.store import Store
from openpipe.templates_msg import render_sequence, render_whatsapp


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


def test_whatsapp_render_is_short():
    wa = render_whatsapp(
        "insurance",
        3,
        prospect_name="Tendai Chirwa",
        company="BrightPath Logistics",
        title="MD",
        trigger="added vans",
        sender_name="Tariro",
        business_name="Horizon",
    )
    assert "Tendai" in wa.body
    assert len(wa.body) < 400


def test_discover_filters_by_vertical_and_city():
    hits = discover(vertical="insurance", city="Harare", niche="fleet", limit=5)
    assert hits
    assert any("fleet" in p.niche_tags or "insurance" in p.niche_tags for p in hits)


def test_plan_and_run_due_dual_channel(tmp_path: Path):
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
        channels="both",
        access_token="",
    )
    prospect = store.add_prospect(
        biz.id,
        full_name="Farai Dube",
        email="farai@steelcity.example",
        phone="+263771234567",
        title="Ops Director",
        company="Steel City",
        trigger="Won a municipal tender",
    )
    engine = OutreachEngine(store, MessageSender(mode="demo"))
    planned = engine.plan_prospect(biz.id, prospect)
    channels = {m.channel for m in planned}
    assert "email" in channels
    assert "whatsapp" in channels
    assert {m.day for m in planned} >= {0, 3, 7}

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
    assert result["by_channel"]["email"] + result["by_channel"]["whatsapp"] == result["sent"]
    assert store.stats(biz.id)["messages_sent"] >= 1


def test_sample_sequences_cover_core_icps():
    from openpipe.templates_msg import sample_sequences

    samples = sample_sequences()
    assert {s["vertical"] for s in samples} == {"insurance", "advisor", "b2b"}
    for sample in samples:
        assert len(sample["days"]) == 3
        bodies = " ".join(d["body"] for d in sample["days"])
        assert sample["prospect"].split()[0] in bodies
        assert all(d.get("whatsapp") for d in sample["days"])


def test_seed_creates_three_icp_kits(tmp_path: Path):
    store = Store(tmp_path / "kits.db")
    store.seed_demo(force=True)
    businesses = store.list_businesses()
    assert len(businesses) == 3
    assert {b.vertical for b in businesses} == {"insurance", "advisor", "b2b"}
    for biz in businesses:
        assert store.list_prospects(biz.id)


def test_register_business(tmp_path: Path):
    store = Store(tmp_path / "reg.db")
    biz = store.register_business(
        owner_name="Dean",
        business_name="Dean Advisory",
        vertical="advisor",
        owner_email="dean@example.com",
        owner_phone="+263770000111",
        channels="both",
        city="Harare",
        niche="executive",
    )
    assert biz.access_token
    assert store.get_business_by_token(biz.access_token).id == biz.id
    assert store.get_business_by_owner_email("dean@example.com").name == "Dean Advisory"


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
