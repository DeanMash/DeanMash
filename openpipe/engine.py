"""Prospect → personalise → send engine (Day 0 / 3 / 7)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from . import config
from .messaging import MessageSender
from .store import OutboundMessage, Prospect, Store
from .templates_msg import DEFAULT_OFFERS, all_days, render_sequence


def _utc(dt: datetime | None = None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class OutreachEngine:
    def __init__(self, store: Store, sender: MessageSender | None = None) -> None:
        self.store = store
        self.sender = sender or MessageSender()

    def plan_prospect(self, business_id: str, prospect: Prospect) -> list[OutboundMessage]:
        biz = self.store.get_business(business_id)
        if not biz:
            return []

        # Anchor Day 0 slightly in the past so demo "Send due" works immediately.
        now = _utc()
        planned: list[OutboundMessage] = []

        for day in all_days():
            copy = render_sequence(
                biz.vertical,
                day,
                prospect_name=prospect.full_name,
                company=prospect.company,
                title=prospect.title,
                trigger=prospect.trigger,
                sender_name=biz.sender_name,
                business_name=biz.name,
                offer=biz.offer or DEFAULT_OFFERS.get(biz.vertical),
                booking_link=biz.booking_link,
            )
            scheduled = now - timedelta(minutes=5) + timedelta(days=day)

            if prospect.status in {"replied", "meeting", "paused"}:
                status = "skipped"
            elif prospect.status == "exhausted":
                status = "skipped"
            else:
                status = "queued"

            msg = OutboundMessage(
                id=str(uuid4()),
                business_id=business_id,
                prospect_id=prospect.id,
                day=day,
                channel="email",
                subject=copy.subject,
                body=copy.body,
                status=status,
                scheduled_for=scheduled.isoformat(),
                sent_at=None,
                error=None,
            )
            self.store.upsert_message(msg)
            planned.append(msg)

        if prospect.status == "new":
            self.store.update_prospect(prospect.id, status="sequenced")
        return planned

    def plan_business(self, business_id: str) -> dict:
        prospects = self.store.list_prospects(business_id)
        total = 0
        for prospect in prospects:
            if prospect.status == "paused":
                continue
            planned = self.plan_prospect(business_id, prospect)
            total += len(planned)
        self.store.add_event(
            business_id,
            "plan",
            {"prospects": len(prospects), "messages_planned": total},
        )
        return {"prospects": len(prospects), "messages_planned": total}

    def discover_and_plan(
        self,
        business_id: str,
        *,
        limit: int = 10,
        city: str | None = None,
        niche: str | None = None,
    ) -> dict:
        added = self.store.find_prospects(
            business_id, city=city, niche=niche, limit=limit
        )
        planned = 0
        for prospect in added:
            planned += len(self.plan_prospect(business_id, prospect))
        return {"added": len(added), "messages_planned": planned}

    def run_due(self, business_id: str | None = None, as_of: datetime | None = None) -> dict:
        now = _utc(as_of)
        due = self.store.due_messages(now)
        if business_id:
            due = [m for m in due if m.business_id == business_id]

        cap = config.DAILY_SEND_CAP
        sent = 0
        failed = 0
        skipped_cap = 0

        for msg in due:
            if sent >= cap:
                skipped_cap += 1
                continue

            prospect = self.store.get_prospect(msg.prospect_id)
            biz = self.store.get_business(msg.business_id)
            if not prospect or not biz:
                self.store.mark_message(msg.id, "failed", "missing prospect or business")
                failed += 1
                continue
            if prospect.status in {"replied", "meeting", "paused"}:
                self.store.mark_message(msg.id, "skipped", "prospect not eligible")
                continue

            result = self.sender.send_email(
                to=prospect.email,
                subject=msg.subject,
                body=msg.body,
                from_email=biz.sender_email,
            )

            if result.ok:
                self.store.mark_message(msg.id, "sent")
                if prospect.status == "new":
                    self.store.update_prospect(prospect.id, status="sequenced")
                if msg.day >= 7:
                    self.store.update_prospect(prospect.id, status="exhausted")
                self.store.add_event(
                    msg.business_id,
                    "message_sent",
                    {
                        "prospect_id": prospect.id,
                        "prospect_name": prospect.full_name,
                        "company": prospect.company,
                        "day": msg.day,
                        "channel": result.channel,
                        "subject": msg.subject,
                    },
                )
                sent += 1
            else:
                self.store.mark_message(msg.id, "failed", result.error)
                failed += 1

        if business_id:
            self.store.add_event(
                business_id,
                "run",
                {
                    "sent": sent,
                    "failed": failed,
                    "skipped_cap": skipped_cap,
                    "as_of": now.isoformat(),
                },
            )
        return {
            "sent": sent,
            "failed": failed,
            "checked": len(due),
            "skipped_cap": skipped_cap,
        }

    def mark_replied(self, prospect_id: str) -> Prospect | None:
        prospect = self.store.update_prospect(
            prospect_id,
            status="replied",
            replied_at=datetime.now(timezone.utc).isoformat(),
        )
        if prospect:
            for msg in self.store.list_messages(prospect.business_id, limit=500):
                if msg.prospect_id == prospect_id and msg.status == "queued":
                    self.store.mark_message(msg.id, "skipped", "replied")
            self.store.add_event(
                prospect.business_id,
                "replied",
                {
                    "prospect_id": prospect.id,
                    "prospect_name": prospect.full_name,
                    "company": prospect.company,
                },
            )
        return prospect

    def mark_meeting(self, prospect_id: str) -> Prospect | None:
        prospect = self.store.update_prospect(
            prospect_id,
            status="meeting",
            replied_at=datetime.now(timezone.utc).isoformat(),
        )
        if prospect:
            for msg in self.store.list_messages(prospect.business_id, limit=500):
                if msg.prospect_id == prospect_id and msg.status == "queued":
                    self.store.mark_message(msg.id, "skipped", "meeting booked")
            self.store.add_event(
                prospect.business_id,
                "meeting",
                {
                    "prospect_id": prospect.id,
                    "prospect_name": prospect.full_name,
                    "company": prospect.company,
                },
            )
        return prospect

    def preview(self, business_id: str, prospect_id: str, day: int = 0) -> dict:
        biz = self.store.get_business(business_id)
        prospect = self.store.get_prospect(prospect_id)
        if not biz or not prospect:
            return {"error": "not found"}
        copy = render_sequence(
            biz.vertical,
            day,
            prospect_name=prospect.full_name,
            company=prospect.company,
            title=prospect.title,
            trigger=prospect.trigger,
            sender_name=biz.sender_name,
            business_name=biz.name,
            offer=biz.offer or DEFAULT_OFFERS.get(biz.vertical),
            booking_link=biz.booking_link,
        )
        return {
            "day": copy.day,
            "subject": copy.subject,
            "body": copy.body,
            "channel": "email",
            "to": prospect.email,
        }
