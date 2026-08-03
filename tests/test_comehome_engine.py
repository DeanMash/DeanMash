from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from comehome.engine import WinBackEngine
from comehome.messaging import MessageSender
from comehome.store import Store
from comehome.templates_msg import render_sequence


def test_render_sequence_personalizes_name():
    copy = render_sequence(
        "gym",
        30,
        client_name="Rudo Moyo",
        business_name="Mukuvisi Movement Studio",
        staff_name="Tariro",
    )
    assert "Rudo" in copy.body
    assert "Tariro" in copy.body
    assert "Mukuvisi" in copy.body


def test_plan_and_run_due(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    biz = store.create_business(
        name="Test Gym",
        vertical="gym",
        city="Harare",
        staff_name="Tariro",
        booking_link="https://wa.me/263770000000",
        offer="Soft restart week",
        plan="studio",
    )
    last = (date.today() - timedelta(days=35)).isoformat()
    client = store.add_client(
        biz.id,
        full_name="Farai Sibanda",
        phone="+263771111111",
        last_visit=last,
        staff_name="Tariro",
    )
    engine = WinBackEngine(store, MessageSender(mode="demo"))
    planned = engine.plan_client(biz.id, client)
    assert len(planned) == 3
    assert {m.day for m in planned} == {30, 60, 90}

    # Force schedule into the past so run_due picks them up.
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


def test_recover_skips_remaining(tmp_path: Path):
    store = Store(tmp_path / "recover.db")
    biz = store.seed_demo(force=True)
    engine = WinBackEngine(store, MessageSender(mode="demo"))
    engine.plan_business(biz.id)
    client = next(c for c in store.list_clients(biz.id) if c.status == "in_sequence")
    engine.mark_recovered(client.id)
    refreshed = store.get_client(client.id)
    assert refreshed is not None
    assert refreshed.status == "recovered"
    queued = [m for m in store.list_messages(biz.id) if m.client_id == client.id and m.status == "queued"]
    assert queued == []
