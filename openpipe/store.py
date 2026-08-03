"""SQLite persistence for businesses, prospects, and outbound emails."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from . import config
from .prospects import discover


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(d: datetime | None) -> str | None:
    if d is None:
        return None
    return d.astimezone(timezone.utc).isoformat()


@dataclass
class Business:
    id: str
    name: str
    vertical: str
    city: str
    sender_name: str
    sender_email: str
    booking_link: str
    offer: str
    plan: str
    niche: str
    created_at: str


@dataclass
class Prospect:
    id: str
    business_id: str
    full_name: str
    email: str
    title: str
    company: str
    industry: str
    city: str
    company_size: str
    trigger: str
    status: str  # new | sequenced | replied | meeting | paused | exhausted
    notes: str
    created_at: str
    replied_at: str | None = None


@dataclass
class OutboundMessage:
    id: str
    business_id: str
    prospect_id: str
    day: int
    channel: str
    subject: str
    body: str
    status: str  # queued | sent | failed | skipped
    scheduled_for: str
    sent_at: str | None
    error: str | None


class Store:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS businesses (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    vertical TEXT NOT NULL,
                    city TEXT NOT NULL,
                    sender_name TEXT NOT NULL,
                    sender_email TEXT NOT NULL,
                    booking_link TEXT NOT NULL,
                    offer TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    niche TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS prospects (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    city TEXT NOT NULL,
                    company_size TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    status TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    replied_at TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
                    prospect_id TEXT NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
                    day INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    sent_at TEXT,
                    error TEXT,
                    UNIQUE(prospect_id, day)
                );

                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def create_business(self, **kwargs: Any) -> Business:
        biz = Business(
            id=kwargs.get("id") or str(uuid4()),
            name=kwargs["name"],
            vertical=kwargs["vertical"],
            city=kwargs.get("city", "Harare"),
            sender_name=kwargs.get("sender_name", "the team"),
            sender_email=kwargs.get("sender_email", "hello@openpipe.example"),
            booking_link=kwargs.get("booking_link", "https://openpipe.example/book"),
            offer=kwargs.get("offer", ""),
            plan=kwargs.get("plan", "starter"),
            niche=kwargs.get("niche", ""),
            created_at=kwargs.get("created_at") or _iso(_utcnow()) or "",
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO businesses
                (id, name, vertical, city, sender_name, sender_email, booking_link, offer, plan, niche, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    biz.id,
                    biz.name,
                    biz.vertical,
                    biz.city,
                    biz.sender_name,
                    biz.sender_email,
                    biz.booking_link,
                    biz.offer,
                    biz.plan,
                    biz.niche,
                    biz.created_at,
                ),
            )
        return biz

    def list_businesses(self) -> list[Business]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM businesses ORDER BY created_at").fetchall()
        return [Business(**dict(r)) for r in rows]

    def get_business(self, business_id: str) -> Business | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM businesses WHERE id = ?", (business_id,)
            ).fetchone()
        return Business(**dict(row)) if row else None

    def add_prospect(self, business_id: str, **kwargs: Any) -> Prospect:
        prospect = Prospect(
            id=kwargs.get("id") or str(uuid4()),
            business_id=business_id,
            full_name=kwargs["full_name"],
            email=kwargs["email"],
            title=kwargs.get("title", ""),
            company=kwargs.get("company", ""),
            industry=kwargs.get("industry", ""),
            city=kwargs.get("city", ""),
            company_size=kwargs.get("company_size", ""),
            trigger=kwargs.get("trigger", ""),
            status=kwargs.get("status", "new"),
            notes=kwargs.get("notes", ""),
            created_at=kwargs.get("created_at") or _iso(_utcnow()) or "",
            replied_at=kwargs.get("replied_at"),
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO prospects
                (id, business_id, full_name, email, title, company, industry, city,
                 company_size, trigger, status, notes, created_at, replied_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prospect.id,
                    prospect.business_id,
                    prospect.full_name,
                    prospect.email,
                    prospect.title,
                    prospect.company,
                    prospect.industry,
                    prospect.city,
                    prospect.company_size,
                    prospect.trigger,
                    prospect.status,
                    prospect.notes,
                    prospect.created_at,
                    prospect.replied_at,
                ),
            )
        return prospect

    def list_prospects(self, business_id: str) -> list[Prospect]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM prospects WHERE business_id = ? ORDER BY created_at DESC",
                (business_id,),
            ).fetchall()
        return [Prospect(**dict(r)) for r in rows]

    def get_prospect(self, prospect_id: str) -> Prospect | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM prospects WHERE id = ?", (prospect_id,)
            ).fetchone()
        return Prospect(**dict(row)) if row else None

    def update_prospect(self, prospect_id: str, **fields: Any) -> Prospect | None:
        if not fields:
            return self.get_prospect(prospect_id)
        cols = ", ".join(f"{k} = ?" for k in fields)
        with self._conn() as conn:
            conn.execute(
                f"UPDATE prospects SET {cols} WHERE id = ?",
                (*fields.values(), prospect_id),
            )
        return self.get_prospect(prospect_id)

    def upsert_message(self, msg: OutboundMessage) -> OutboundMessage:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO messages
                (id, business_id, prospect_id, day, channel, subject, body, status, scheduled_for, sent_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(prospect_id, day) DO UPDATE SET
                    subject=excluded.subject,
                    body=excluded.body,
                    status=excluded.status,
                    scheduled_for=excluded.scheduled_for,
                    sent_at=excluded.sent_at,
                    error=excluded.error
                """,
                (
                    msg.id,
                    msg.business_id,
                    msg.prospect_id,
                    msg.day,
                    msg.channel,
                    msg.subject,
                    msg.body,
                    msg.status,
                    msg.scheduled_for,
                    msg.sent_at,
                    msg.error,
                ),
            )
        return msg

    def list_messages(self, business_id: str, limit: int = 100) -> list[OutboundMessage]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE business_id = ?
                ORDER BY scheduled_for DESC
                LIMIT ?
                """,
                (business_id, limit),
            ).fetchall()
        return [OutboundMessage(**dict(r)) for r in rows]

    def due_messages(self, as_of: datetime | None = None) -> list[OutboundMessage]:
        now = _iso(as_of or _utcnow()) or ""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE status = 'queued' AND scheduled_for <= ?
                ORDER BY scheduled_for
                """,
                (now,),
            ).fetchall()
        return [OutboundMessage(**dict(r)) for r in rows]

    def mark_message(self, message_id: str, status: str, error: str | None = None) -> None:
        sent_at = _iso(_utcnow()) if status == "sent" else None
        with self._conn() as conn:
            conn.execute(
                "UPDATE messages SET status = ?, sent_at = ?, error = ? WHERE id = ?",
                (status, sent_at, error, message_id),
            )

    def add_event(self, business_id: str, kind: str, payload: dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO events (id, business_id, kind, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                (str(uuid4()), business_id, kind, json.dumps(payload), _iso(_utcnow())),
            )

    def recent_events(self, business_id: str, limit: int = 40) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM events
                WHERE business_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (business_id, limit),
            ).fetchall()
        out = []
        for r in rows:
            item = dict(r)
            item["payload"] = json.loads(item["payload"])
            out.append(item)
        return out

    def stats(self, business_id: str) -> dict[str, Any]:
        prospects = self.list_prospects(business_id)
        messages = self.list_messages(business_id, limit=2000)
        sent = [m for m in messages if m.status == "sent"]
        queued = [m for m in messages if m.status == "queued"]
        replied = [p for p in prospects if p.status == "replied"]
        meetings = [p for p in prospects if p.status == "meeting"]
        sequenced = [p for p in prospects if p.status == "sequenced"]
        return {
            "prospects": len(prospects),
            "sequenced": len(sequenced),
            "replied": len(replied),
            "meetings": len(meetings),
            "messages_sent": len(sent),
            "messages_queued": len(queued),
            "reply_rate": round((len(replied) / len(prospects)) * 100, 1) if prospects else 0.0,
            "at_day0": len([m for m in queued if m.day == 0]),
            "at_day3": len([m for m in queued if m.day == 3]),
            "at_day7": len([m for m in queued if m.day == 7]),
        }

    def find_prospects(
        self,
        business_id: str,
        *,
        vertical: str | None = None,
        city: str | None = None,
        niche: str | None = None,
        limit: int = 10,
    ) -> list[Prospect]:
        """Discover from the pool and upsert into this business's pipeline."""
        biz = self.get_business(business_id)
        if not biz:
            return []
        seeds = discover(
            vertical=vertical or biz.vertical,
            city=city if city is not None else biz.city,
            niche=niche if niche is not None else biz.niche,
            limit=limit,
        )
        existing_emails = {p.email.lower() for p in self.list_prospects(business_id)}
        added: list[Prospect] = []
        for seed in seeds:
            if seed.email.lower() in existing_emails:
                continue
            prospect = self.add_prospect(
                business_id,
                full_name=seed.full_name,
                email=seed.email,
                title=seed.title,
                company=seed.company,
                industry=seed.industry,
                city=seed.city,
                company_size=seed.company_size,
                trigger=seed.trigger,
                status="new",
                notes=f"Discovered · {seed.industry} · {seed.company_size}",
            )
            existing_emails.add(seed.email.lower())
            added.append(prospect)
        self.add_event(
            business_id,
            "discover",
            {
                "added": len(added),
                "vertical": vertical or biz.vertical,
                "city": city if city is not None else biz.city,
                "niche": niche if niche is not None else biz.niche,
            },
        )
        return added

    def seed_demo(self, force: bool = False) -> Business:
        existing = self.list_businesses()
        if existing and not force:
            return existing[0]

        if force:
            with self._conn() as conn:
                conn.executescript(
                    "DELETE FROM messages; DELETE FROM prospects; DELETE FROM events; DELETE FROM businesses;"
                )

        biz = self.create_business(
            id="demo-broker",
            name="Horizon Cover Brokers",
            vertical="insurance",
            city="Harare",
            sender_name="Tariro Moyo",
            sender_email="tariro@horizoncover.example",
            booking_link="https://cal.example/horizon-cover",
            offer="a 20-minute cover gap review for your business",
            plan="pipeline",
            niche="fleet logistics sme",
        )

        # Preload a few discovered prospects in varied pipeline states.
        seeded = self.find_prospects(biz.id, limit=8)
        # Mark one as replied / meeting for dashboard realism.
        if len(seeded) >= 2:
            self.update_prospect(
                seeded[0].id,
                status="replied",
                replied_at=_iso(_utcnow()),
                notes="Replied — interested in fleet review",
            )
        if len(seeded) >= 3:
            self.update_prospect(
                seeded[1].id,
                status="meeting",
                replied_at=_iso(_utcnow()),
                notes="Meeting booked Thursday 10:00",
            )

        self.add_event(
            biz.id,
            "seed",
            {"message": "Demo insurance brokerage seeded with Harare SME prospects"},
        )
        return biz


def prospect_to_dict(p: Prospect) -> dict[str, Any]:
    return asdict(p)
