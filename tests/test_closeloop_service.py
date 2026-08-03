from datetime import date, timedelta

import closeloop.db as db_module
from closeloop.messaging import MessageSender
from closeloop.service import (
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
    assert any(c.channel == "call_script" for c in trade.sequences)


def test_next_follow_up_date_progression():
    quoted = date(2026, 1, 1)
    assert next_follow_up_date(quoted, today=date(2026, 1, 1)) == date(2026, 1, 3)
    assert next_follow_up_date(quoted, today=date(2026, 1, 4)) == date(2026, 1, 6)
    assert next_follow_up_date(quoted, today=date(2026, 1, 12)) is None


def test_create_estimate_schedules_day_2_5_10():
    with db_module.SessionLocal() as db:
        biz = create_business(db, name="Paint Pros", owner_name="Ana", trade_key="painting")
        est = create_estimate(
            db,
            biz,
            homeowner_name="Sam Lee",
            homeowner_phone="+15550001111",
            homeowner_email="sam@example.com",
            address="1 Main",
            amount=4500,
            quoted_on=date.today() - timedelta(days=1),
        )
        assert est.status == "open"
        assert len(est.follow_ups) == 8  # sms+email on 2; sms+email+call on 5 & 10
        assert {fu.day for fu in est.follow_ups} == {2, 5, 10}
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
        )
        set_estimate_status(db, est, "lost", lost_reason="Chose competitor who called back")
        assert est.lost_reason.startswith("Chose competitor")
        assert all(fu.status == "skipped" for fu in est.follow_ups)