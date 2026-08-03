"""SQLite persistence for businesses, clients, and outbound messages."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from . import config


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(d: date | datetime | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.astimezone(timezone.utc).isoformat()
    return d.isoformat()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


@dataclass
class Business:
    id: str
    name: str
    vertical: str
    city: str
    staff_name: str
    booking_link: str
    offer: str
    plan: str
    whatsapp_from: str
    created_at: str


@dataclass
class Client:
    id: str
    business_id: str
    full_name: str
    phone: str
    last_visit: str
    status: str  # active | in_sequence | recovered | paused | exhausted
    staff_name: str
    notes: str
    created_at: str
    recovered_at: str | None = None


@dataclass
class OutboundMessage:
    id: str
    business_id: str
    client_id: str
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
                    staff_name TEXT NOT NULL,
                    booking_link TEXT NOT NULL,
                    offer TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    whatsapp_from TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    last_visit TEXT NOT NULL,
                    status TEXT NOT NULL,
                    staff_name TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    recovered_at TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
                    client_id TEXT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
                    day INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    sent_at TEXT,
                    error TEXT,
                    UNIQUE(client_id, day)
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
            staff_name=kwargs.get("staff_name", "the team"),
            booking_link=kwargs.get("booking_link", "https://comehome.example/book"),
            offer=kwargs.get("offer", ""),
            plan=kwargs.get("plan", "studio"),
            whatsapp_from=kwargs.get("whatsapp_from", "+263770000000"),
            created_at=kwargs.get("created_at") or _iso(_utcnow()) or "",
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO businesses
                (id, name, vertical, city, staff_name, booking_link, offer, plan, whatsapp_from, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    biz.id,
                    biz.name,
                    biz.vertical,
                    biz.city,
                    biz.staff_name,
                    biz.booking_link,
                    biz.offer,
                    biz.plan,
                    biz.whatsapp_from,
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

    def add_client(self, business_id: str, **kwargs: Any) -> Client:
        client = Client(
            id=kwargs.get("id") or str(uuid4()),
            business_id=business_id,
            full_name=kwargs["full_name"],
            phone=kwargs["phone"],
            last_visit=kwargs["last_visit"],
            status=kwargs.get("status", "active"),
            staff_name=kwargs.get("staff_name", ""),
            notes=kwargs.get("notes", ""),
            created_at=kwargs.get("created_at") or _iso(_utcnow()) or "",
            recovered_at=kwargs.get("recovered_at"),
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO clients
                (id, business_id, full_name, phone, last_visit, status, staff_name, notes, created_at, recovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    client.id,
                    client.business_id,
                    client.full_name,
                    client.phone,
                    client.last_visit,
                    client.status,
                    client.staff_name,
                    client.notes,
                    client.created_at,
                    client.recovered_at,
                ),
            )
        return client

    def list_clients(self, business_id: str) -> list[Client]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM clients WHERE business_id = ? ORDER BY last_visit",
                (business_id,),
            ).fetchall()
        return [Client(**dict(r)) for r in rows]

    def get_client(self, client_id: str) -> Client | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        return Client(**dict(row)) if row else None

    def update_client(self, client_id: str, **fields: Any) -> Client | None:
        if not fields:
            return self.get_client(client_id)
        cols = ", ".join(f"{k} = ?" for k in fields)
        with self._conn() as conn:
            conn.execute(
                f"UPDATE clients SET {cols} WHERE id = ?",
                (*fields.values(), client_id),
            )
        return self.get_client(client_id)

    def upsert_message(self, msg: OutboundMessage) -> OutboundMessage:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO messages
                (id, business_id, client_id, day, channel, subject, body, status, scheduled_for, sent_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(client_id, day) DO UPDATE SET
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
                    msg.client_id,
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
        clients = self.list_clients(business_id)
        messages = self.list_messages(business_id, limit=1000)
        today = date.today()

        def days_since(c: Client) -> int:
            lv = _parse_date(c.last_visit)
            return (today - lv).days if lv else 0

        lapsing = [c for c in clients if days_since(c) >= 30 and c.status != "recovered"]
        recovered = [c for c in clients if c.status == "recovered"]
        sent = [m for m in messages if m.status == "sent"]
        queued = [m for m in messages if m.status == "queued"]
        return {
            "clients": len(clients),
            "lapsing": len(lapsing),
            "recovered": len(recovered),
            "messages_sent": len(sent),
            "messages_queued": len(queued),
            "recovery_rate": round((len(recovered) / len(clients)) * 100, 1) if clients else 0.0,
            "at_30": len([c for c in lapsing if 30 <= days_since(c) < 60]),
            "at_60": len([c for c in lapsing if 60 <= days_since(c) < 90]),
            "at_90": len([c for c in lapsing if days_since(c) >= 90]),
        }

    def seed_demo(self, force: bool = False) -> Business:
        existing = self.list_businesses()
        if existing and not force:
            return existing[0]

        if force:
            with self._conn() as conn:
                conn.executescript(
                    "DELETE FROM messages; DELETE FROM clients; DELETE FROM events; DELETE FROM businesses;"
                )

        biz = self.create_business(
            id="demo-studio",
            name="Mukuvisi Movement Studio",
            vertical="gym",
            city="Harare",
            staff_name="Tariro",
            booking_link="https://wa.me/263771234567",
            offer="Your first week back is on a soft restart rate",
            plan="practice",
            whatsapp_from="+263771234567",
        )

        today = date.today()
        demo_clients = [
            ("Rudo Moyo", "+263772111001", 34, "in_sequence", "Prefers evening classes"),
            ("Tinashe Ncube", "+263773222002", 48, "in_sequence", "Was on PT with Tariro"),
            ("Chiedza Dube", "+263774333003", 67, "in_sequence", "Maternity pause — gentle return"),
            ("Farai Sibanda", "+263775444004", 95, "in_sequence", "Moved to Borrowdale"),
            ("Nyasha Gumbo", "+263776555005", 12, "active", "Regular — no outreach yet"),
            ("Blessing Mhlanga", "+263777666006", 41, "recovered", "Came back after day-30 note"),
            ("Tatenda Chirwa", "+263778777007", 72, "in_sequence", "Corporate package lapsed"),
            ("Aisha Patel", "+263779888008", 110, "exhausted", "Completed 90-day sequence"),
            ("Kudzai Banda", "+263771999009", 55, "in_sequence", "Yoga + weights"),
            ("Sean Williams", "+263770101010", 28, "active", "Borderline — watches soon"),
        ]
        for name, phone, ago, status, notes in demo_clients:
            self.add_client(
                biz.id,
                full_name=name,
                phone=phone,
                last_visit=(today - timedelta(days=ago)).isoformat(),
                status=status,
                staff_name="Tariro",
                notes=notes,
                recovered_at=_iso(_utcnow()) if status == "recovered" else None,
            )
        self.add_event(
            biz.id,
            "seed",
            {"message": "Demo business seeded with Zimbabwe-style client roster"},
        )
        return biz


def days_since_visit(last_visit: str, today: date | None = None) -> int:
    lv = _parse_date(last_visit)
    if not lv:
        return 0
    return ((today or date.today()) - lv).days


def client_to_dict(c: Client) -> dict[str, Any]:
    d = asdict(c)
    d["days_since_visit"] = days_since_visit(c.last_visit)
    return d
