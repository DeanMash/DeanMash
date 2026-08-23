"""SQLite persistence for orgs, prospects, and outbound email/WhatsApp."""

from __future__ import annotations

import json
import secrets
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from . import config
from .channels import normalize_channels
from .prospects import discover
from .starters import STARTERS


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(d: datetime | None) -> str | None:
    if d is None:
        return None
    return d.astimezone(timezone.utc).isoformat()


def _demo_phone(email: str) -> str:
    n = sum(ord(c) for c in email) % 10_000_000
    return f"+26377{n:07d}"


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
    access_token: str = ""
    owner_email: str = ""
    owner_phone: str = ""
    channels: str = "both"
    whatsapp_from: str = ""
    auto_run: int = 1


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
    phone: str = ""


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


def _business_from_row(row: sqlite3.Row | dict) -> Business:
    d = dict(row)
    return Business(
        id=d["id"],
        name=d["name"],
        vertical=d["vertical"],
        city=d["city"],
        sender_name=d["sender_name"],
        sender_email=d["sender_email"],
        booking_link=d["booking_link"],
        offer=d["offer"],
        plan=d["plan"],
        niche=d["niche"],
        created_at=d["created_at"],
        access_token=d.get("access_token") or "",
        owner_email=d.get("owner_email") or "",
        owner_phone=d.get("owner_phone") or "",
        channels=normalize_channels(d.get("channels") or "both"),
        whatsapp_from=d.get("whatsapp_from") or "",
        auto_run=int(d["auto_run"]) if d.get("auto_run") is not None else 1,
    )


def _prospect_from_row(row: sqlite3.Row | dict) -> Prospect:
    d = dict(row)
    return Prospect(
        id=d["id"],
        business_id=d["business_id"],
        full_name=d["full_name"],
        email=d["email"],
        title=d["title"],
        company=d["company"],
        industry=d["industry"],
        city=d["city"],
        company_size=d["company_size"],
        trigger=d["trigger"],
        status=d["status"],
        notes=d.get("notes") or "",
        created_at=d["created_at"],
        replied_at=d.get("replied_at"),
        phone=d.get("phone") or "",
    )


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
                    created_at TEXT NOT NULL,
                    access_token TEXT NOT NULL DEFAULT '',
                    owner_email TEXT NOT NULL DEFAULT '',
                    owner_phone TEXT NOT NULL DEFAULT '',
                    channels TEXT NOT NULL DEFAULT 'both',
                    whatsapp_from TEXT NOT NULL DEFAULT '',
                    auto_run INTEGER NOT NULL DEFAULT 1
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
                    replied_at TEXT,
                    phone TEXT NOT NULL DEFAULT ''
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
                    UNIQUE(prospect_id, day, channel)
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
            self._migrate(conn)

    def _migrate(self, conn: sqlite3.Connection) -> None:
        biz_cols = {r[1] for r in conn.execute("PRAGMA table_info(businesses)").fetchall()}
        for col, ddl in [
            ("access_token", "TEXT NOT NULL DEFAULT ''"),
            ("owner_email", "TEXT NOT NULL DEFAULT ''"),
            ("owner_phone", "TEXT NOT NULL DEFAULT ''"),
            ("channels", "TEXT NOT NULL DEFAULT 'both'"),
            ("whatsapp_from", "TEXT NOT NULL DEFAULT ''"),
            ("auto_run", "INTEGER NOT NULL DEFAULT 1"),
        ]:
            if col not in biz_cols:
                conn.execute(f"ALTER TABLE businesses ADD COLUMN {col} {ddl}")

        prospect_cols = {r[1] for r in conn.execute("PRAGMA table_info(prospects)").fetchall()}
        if "phone" not in prospect_cols:
            conn.execute("ALTER TABLE prospects ADD COLUMN phone TEXT NOT NULL DEFAULT ''")

        # Upgrade messages unique key from (prospect_id, day) → (prospect_id, day, channel).
        indexes = conn.execute("PRAGMA index_list(messages)").fetchall()
        needs_rebuild = False
        for idx in indexes:
            name = idx[1]
            unique = idx[2]
            if not unique:
                continue
            cols = [r[2] for r in conn.execute(f"PRAGMA index_info('{name}')").fetchall()]
            if cols == ["prospect_id", "day"]:
                needs_rebuild = True
                break
        # Also rebuild if table SQL still has old UNIQUE (no channel in unique).
        create_sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='messages'"
        ).fetchone()
        if create_sql and create_sql[0] and "UNIQUE(prospect_id, day)" in create_sql[0].replace(
            " ", ""
        ).replace("\n", ""):
            # match UNIQUE(prospect_id, day) without channel
            if "UNIQUE(prospect_id,day,channel)" not in create_sql[0].replace(" ", "").replace(
                "\n", ""
            ):
                if "UNIQUE(prospect_id, day)" in create_sql[0] or "UNIQUE(prospect_id,day)" in create_sql[
                    0
                ].replace(" ", ""):
                    needs_rebuild = True

        if needs_rebuild:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS messages_v2 (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    prospect_id TEXT NOT NULL,
                    day INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    sent_at TEXT,
                    error TEXT,
                    UNIQUE(prospect_id, day, channel)
                );
                INSERT OR IGNORE INTO messages_v2
                SELECT id, business_id, prospect_id, day, channel, subject, body,
                       status, scheduled_for, sent_at, error
                FROM messages;
                DROP TABLE messages;
                ALTER TABLE messages_v2 RENAME TO messages;
                """
            )

    def create_business(self, **kwargs: Any) -> Business:
        token = kwargs.get("access_token")
        if token is None:
            token = secrets.token_urlsafe(18)
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
            access_token=token or "",
            owner_email=kwargs.get("owner_email", ""),
            owner_phone=kwargs.get("owner_phone", ""),
            channels=normalize_channels(kwargs.get("channels", "both")),
            whatsapp_from=kwargs.get("whatsapp_from", kwargs.get("owner_phone", "")),
            auto_run=int(kwargs.get("auto_run", 1)),
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO businesses
                (id, name, vertical, city, sender_name, sender_email, booking_link, offer, plan, niche,
                 created_at, access_token, owner_email, owner_phone, channels, whatsapp_from, auto_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    biz.access_token,
                    biz.owner_email,
                    biz.owner_phone,
                    biz.channels,
                    biz.whatsapp_from,
                    biz.auto_run,
                ),
            )
        return biz

    def register_business(self, **kwargs: Any) -> Business:
        """Public signup for a small organisation."""
        owner_email = (kwargs.get("owner_email") or kwargs.get("email") or "").strip().lower()
        if owner_email:
            existing = self.get_business_by_owner_email(owner_email)
            if existing:
                raise ValueError("An organisation is already registered with that email")
        name = kwargs.get("name") or kwargs.get("business_name")
        if not name:
            raise ValueError("Business name is required")
        sender_name = kwargs.get("sender_name") or kwargs.get("owner_name") or "the team"
        sender_email = kwargs.get("sender_email") or owner_email or "hello@openpipe.example"
        biz = self.create_business(
            name=name,
            vertical=kwargs.get("vertical", "b2b"),
            city=kwargs.get("city", "Harare"),
            sender_name=sender_name,
            sender_email=sender_email,
            booking_link=kwargs.get("booking_link")
            or f"https://openpipe.example/book/{uuid4().hex[:8]}",
            offer=kwargs.get("offer", ""),
            plan=kwargs.get("plan", "starter"),
            niche=kwargs.get("niche", ""),
            owner_email=owner_email,
            owner_phone=kwargs.get("owner_phone") or kwargs.get("phone") or "",
            channels=kwargs.get("channels", "both"),
            whatsapp_from=kwargs.get("whatsapp_from")
            or kwargs.get("owner_phone")
            or kwargs.get("phone")
            or "",
            auto_run=int(kwargs.get("auto_run", 1)),
        )
        self.add_event(
            biz.id,
            "register",
            {
                "name": biz.name,
                "vertical": biz.vertical,
                "channels": biz.channels,
                "owner_email": biz.owner_email,
            },
        )
        return biz

    def list_businesses(self) -> list[Business]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM businesses ORDER BY created_at").fetchall()
        return [_business_from_row(r) for r in rows]

    def get_business(self, business_id: str) -> Business | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM businesses WHERE id = ?", (business_id,)
            ).fetchone()
        return _business_from_row(row) if row else None

    def get_business_by_token(self, token: str) -> Business | None:
        if not token:
            return None
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM businesses WHERE access_token = ? AND access_token != ''",
                (token,),
            ).fetchone()
        return _business_from_row(row) if row else None

    def get_business_by_owner_email(self, email: str) -> Business | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM businesses WHERE lower(owner_email) = ?",
                (email.lower(),),
            ).fetchone()
        return _business_from_row(row) if row else None

    def update_business(self, business_id: str, **fields: Any) -> Business | None:
        if "channels" in fields:
            fields["channels"] = normalize_channels(fields["channels"])
        if not fields:
            return self.get_business(business_id)
        cols = ", ".join(f"{k} = ?" for k in fields)
        with self._conn() as conn:
            conn.execute(
                f"UPDATE businesses SET {cols} WHERE id = ?",
                (*fields.values(), business_id),
            )
        return self.get_business(business_id)

    def add_prospect(self, business_id: str, **kwargs: Any) -> Prospect:
        prospect = Prospect(
            id=kwargs.get("id") or str(uuid4()),
            business_id=business_id,
            full_name=kwargs["full_name"],
            email=kwargs.get("email", ""),
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
            phone=kwargs.get("phone", ""),
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO prospects
                (id, business_id, full_name, email, title, company, industry, city,
                 company_size, trigger, status, notes, created_at, replied_at, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    prospect.phone,
                ),
            )
        return prospect

    def list_prospects(self, business_id: str) -> list[Prospect]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM prospects WHERE business_id = ? ORDER BY created_at DESC",
                (business_id,),
            ).fetchall()
        return [_prospect_from_row(r) for r in rows]

    def get_prospect(self, prospect_id: str) -> Prospect | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM prospects WHERE id = ?", (prospect_id,)
            ).fetchone()
        return _prospect_from_row(row) if row else None

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
                ON CONFLICT(prospect_id, day, channel) DO UPDATE SET
                    subject=excluded.subject,
                    body=excluded.body,
                    status=excluded.status,
                    scheduled_for=excluded.scheduled_for,
                    sent_at=excluded.sent_at,
                    error=excluded.error,
                    id=excluded.id
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
            "email_sent": len([m for m in sent if m.channel == "email"]),
            "whatsapp_sent": len([m for m in sent if m.channel == "whatsapp"]),
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
            phone = getattr(seed, "phone", "") or _demo_phone(seed.email)
            prospect = self.add_prospect(
                business_id,
                full_name=seed.full_name,
                email=seed.email,
                phone=phone,
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

    def _seed_kit(self, kit_id: str) -> Business | None:
        """Create one ICP starter kit with sample prospects if missing."""
        kit = next((s for s in STARTERS if s.id == kit_id), None)
        if not kit:
            return None
        existing = self.get_business(kit.id)
        if existing:
            return existing

        biz = self.create_business(
            id=kit.id,
            name=kit.name,
            vertical=kit.vertical,
            city=kit.city,
            sender_name=kit.sender_name,
            sender_email=kit.sender_email,
            booking_link=kit.booking_link,
            offer=kit.offer,
            plan=kit.plan,
            niche=kit.niche,
            access_token="",  # open demo kits
            channels="both",
            owner_phone="+263771000000",
            whatsapp_from="+263771000000",
            auto_run=0,
        )
        seeded = self.find_prospects(biz.id, limit=8)
        if len(seeded) >= 2:
            self.update_prospect(
                seeded[0].id,
                status="replied",
                replied_at=_iso(_utcnow()),
                notes="Replied — wants to continue the conversation",
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
            {
                "message": f"Demo {kit.vertical} book seeded",
                "blurb": kit.blurb,
                "start_tip": kit.start_tip,
            },
        )
        return biz

    def seed_demo(self, force: bool = False) -> Business:
        """Ensure insurance / advisor / B2B starter kits exist; return insurance."""
        if force:
            with self._conn() as conn:
                conn.executescript(
                    "DELETE FROM messages; DELETE FROM prospects; DELETE FROM events; DELETE FROM businesses;"
                )

        existing_by_vertical = {
            b.vertical: b for b in self.list_businesses() if b.id.startswith("demo-")
        }
        existing_ids = {b.id for b in self.list_businesses()}

        for kit in STARTERS:
            if kit.id in existing_ids:
                continue
            if kit.vertical in existing_by_vertical:
                continue
            self._seed_kit(kit.id)

        businesses = self.list_businesses()
        for biz in businesses:
            if biz.vertical == "insurance" or biz.id in {"demo-insurance", "demo-broker"}:
                return biz
        if businesses:
            return businesses[0]
        raise RuntimeError("Failed to seed OpenPipe demo kits")


def prospect_to_dict(p: Prospect) -> dict[str, Any]:
    return asdict(p)


def business_to_dict(b: Business, *, include_token: bool = False) -> dict[str, Any]:
    data = asdict(b)
    if not include_token:
        data.pop("access_token", None)
    return data
