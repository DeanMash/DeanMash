from datetime import date, timedelta

import closeloop.db as db_module
from closeloop.messaging import MessageSender
from closeloop.service import (
    authenticate_business,
    create_business,
    create_estimate,
    next_follow_up_date,
    pipeline_stats,
    process_due_follow_ups,
    set_estimate_status,
)
from closeloop.trades import FOLLOW_UP_DAYS, get_trade, list_trades


def setup_function():
    db_module.init_db("sqlite:///:memory:")


def test_trade_catalog_covers_core_verticals():
    keys = {t.key for t in list_trades()}
    for required in ("roofing", "painting", "landscaping", "general_construction", "hvac"):
        assert required in keys
    trade = get_trade("roofing")
    days = {c.day for c in trade.sequences}
    assert days == set(FOLLOW_UP_DAYS)
    assert any(c.channel == "whatsapp" for c in trade.sequences)
    assert any(c.channel == "email" for c in trade.sequences)
    assert any(c.channel == "call_script" for c in trade.sequences)


def test_next_follow_up_date_progression():
    quoted = date(2026, 1, 1)
    assert next_follow_up_date(quoted, today=date(2026, 1, 1)) == date(2026, 1, 3)
    assert next_follow_up_date(quoted, today=date(2026, 1, 4)) == date(2026, 1, 6)
    assert next_follow_up_date(quoted, today=date(2026, 1, 12)) is None


def test_register_business_and_schedule_whatsapp_email():
    with db_module.SessionLocal() as db:
        biz = create_business(
            db,
            name="Paint Pros",
            owner_name="Ana",
            trade_key="painting",
            login_email="ana@paint.test",
            password="secret12",
        )
        assert authenticate_business(db, "ana@paint.test", "secret12")
        assert authenticate_business(db, "ana@paint.test", "nope") is None

        est = create_estimate(
            db,
            biz,
            homeowner_name="Sam Lee",
            homeowner_phone="+15550001111",
            homeowner_email="sam@example.com",
            address="1 Main",
            amount=4500,
            quoted_on=date.today() - timedelta(days=1),
            send_due_now=False,
        )
        assert est.status == "open"
        channels = {fu.channel for fu in est.follow_ups}
        assert "whatsapp" in channels and "email" in channels
        assert any(fu.day == 0 for fu in est.follow_ups)
        assert {fu.day for fu in est.follow_ups} >= {0, 2, 5, 10}
        assert "Sam" in est.follow_ups[0].body
        assert "Paint Pros" in est.follow_ups[0].body


def test_process_due_follow_ups_and_close_won():
    with db_module.SessionLocal() as db:
        biz = create_business(db, name="GreenScape", owner_name="Dee", trade_key="landscaping")
        quoted = date.today() - timedelta(days=5)
        est = create_estimate(
            db,
            biz,
            homeowner_name="Jordan Miles",
            homeowner_phone="+15550002222",
            homeowner_email="jordan@example.com",
            address="9 Oak",
            amount=3200,
            quoted_on=quoted,
            send_due_now=False,
        )
        stats = process_due_follow_ups(db, sender=MessageSender())
        assert stats["processed"] >= 1
        assert stats["sent"] >= 1

        set_estimate_status(db, est, "won")
        db.refresh(est)
        assert est.status == "won"
        assert all(fu.status != "pending" for fu in est.follow_ups)

        pipe = pipeline_stats(db, biz.id)
        assert pipe["won_count"] == 1
        assert pipe["won_value"] == 3200


def test_lost_status_skips_remaining():
    with db_module.SessionLocal() as db:
        biz = create_business(db, name="Volt Electric", owner_name="Kim", trade_key="electrical")
        est = create_estimate(
            db,
            biz,
            homeowner_name="Pat",
            amount=900,
            quoted_on=date.today(),
            send_due_now=False,
        )
        set_estimate_status(db, est, "lost", lost_reason="Chose competitor who called back")
        assert est.lost_reason.startswith("Chose competitor")
        assert all(fu.status == "skipped" for fu in est.follow_ups)


def test_auto_send_on_create():
    with db_module.SessionLocal() as db:
        biz = create_business(db, name="Fence Co", owner_name="Bo", trade_key="fencing")
        est = create_estimate(
            db,
            biz,
            homeowner_name="Pat Client",
            homeowner_phone="+15550003333",
            homeowner_email="pat@example.com",
            amount=2100,
            quoted_on=date.today(),
            send_due_now=True,
        )
        sentish = [fu for fu in est.follow_ups if fu.day == 0]
        assert sentish
        assert all(fu.status in {"sent", "skipped", "failed"} for fu in sentish)