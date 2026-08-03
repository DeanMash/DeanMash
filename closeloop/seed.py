from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from closeloop.models import Business
from closeloop.service import create_business, create_estimate, set_estimate_status


def seed_demo(db: Session) -> Business:
    existing = db.scalar(select(Business).limit(1))
    if existing:
        return existing

    biz = create_business(
        db,
        name="Summit Shield Roofing",
        owner_name="Marcus Hill",
        phone="(555) 014-2200",
        email="marcus@summitshield.example",
        trade_key="roofing",
        plan_key="growth",
    )

    today = date.today()
    samples = [
        {
            "homeowner_name": "Paula Nguyen",
            "homeowner_phone": "+15550140001",
            "homeowner_email": "paula@example.com",
            "address": "18 Cedar Lane",
            "job_title": "Full tear-off architectural shingles",
            "amount": 14200,
            "quoted_on": today - timedelta(days=2),
        },
        {
            "homeowner_name": "James Ortiz",
            "homeowner_phone": "+15550140002",
            "homeowner_email": "james@example.com",
            "address": "904 Maple Ave",
            "job_title": "Storm damage repair + ridge vent",
            "amount": 6800,
            "quoted_on": today - timedelta(days=5),
        },
        {
            "homeowner_name": "Rita Coleman",
            "homeowner_phone": "+15550140003",
            "homeowner_email": "rita@example.com",
            "address": "55 Harbor Rd",
            "job_title": "Metal roof overlay consult",
            "amount": 21500,
            "quoted_on": today - timedelta(days=10),
        },
        {
            "homeowner_name": "Owen Blake",
            "homeowner_phone": "+15550140004",
            "homeowner_email": "owen@example.com",
            "address": "12 Birch Ct",
            "job_title": "Garage + porch re-roof",
            "amount": 9100,
            "quoted_on": today - timedelta(days=1),
        },
        {
            "homeowner_name": "Helen Park",
            "homeowner_phone": "+15550140005",
            "homeowner_email": "helen@example.com",
            "address": "401 Lakeview",
            "job_title": "Insurance supplement roof",
            "amount": 16750,
            "quoted_on": today - timedelta(days=12),
            "status": "won",
        },
        {
            "homeowner_name": "Chris Adler",
            "homeowner_phone": "+15550140006",
            "homeowner_email": "chris@example.com",
            "address": "88 Pine St",
            "job_title": "Soft wash + spot repair",
            "amount": 2400,
            "quoted_on": today - timedelta(days=14),
            "status": "lost",
            "lost_reason": "No follow-up — went with competitor who called",
        },
    ]

    for row in samples:
        status = row.pop("status", None)
        lost_reason = row.pop("lost_reason", "")
        est = create_estimate(db, biz, **row)
        if status:
            set_estimate_status(db, est, status, lost_reason=lost_reason)

    return biz