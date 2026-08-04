"""30 / 60 / 90 day win-back cadence engine."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from .messaging import MessageSender
from .store import Client, OutboundMessage, Store, days_since_visit
from .templates_msg import DEFAULT_OFFERS, all_days, render_sequence


def _utc(dt: datetime | None = None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class WinBackEngine:
    def __init__(self, store: Store, sender: MessageSender | None = None) -> None:
        self.store = store
        self.sender = sender or MessageSender()

    def plan_client(self, business_id: str, client: Client) -> list[OutboundMessage]:
        biz = self.store.get_business(business_id)
        if not biz:
            return []

        last = date.fromisoformat(client.last_visit[:10])
        staff = client.staff_name or biz.staff_name
        planned: list[OutboundMessage] = []

        for day in all_days():
            copy = render_sequence(
                biz.vertical,
                day,
                client_name=client.full_name,
                business_name=biz.name,
                staff_name=staff,
                offer=biz.offer or DEFAULT_OFFERS.get(biz.vertical),
                booking_link=biz.booking_link,
            )
            scheduled = datetime.combine(
                last + timedelta(days=day),
                datetime.min.time(),
                tzinfo=timezone.utc,
            ) + timedelta(hours=9)  # ~09:00 CAT-ish window

            # Already recovered clients should not keep getting mail.
            status = "skipped" if client.status == "recovered" else "queued"
            # Past due but not yet sent — keep queued so runner can send.
            if client.status == "exhausted" and days_since_visit(client.last_visit) > 90:
                # Keep historical plan but don't re-queue new noise.
                status = "skipped"

            msg = OutboundMessage(
                id=str(uuid4()),
                business_id=business_id,
                client_id=client.id,
                day=day,
                channel="whatsapp",
                subject=copy.subject,
                body=copy.body,
                status=status,
                scheduled_for=scheduled.isoformat(),
                sent_at=None,
                error=None,
            )
            self.store.upsert_message(msg)
            planned.append(msg)

        if client.status == "active" and days_since_visit(client.last_visit) >= 30:
            self.store.update_client(client.id, status="in_sequence")
        return planned

    def plan_business(self, business_id: str) -> dict:
        clients = self.store.list_clients(business_id)
        total = 0
        for client in clients:
            if client.status == "paused":
                continue
            planned = self.plan_client(business_id, client)
            total += len(planned)
        self.store.add_event(
            business_id,
            "plan",
            {"clients": len(clients), "messages_planned": total},
        )
        return {"clients": len(clients), "messages_planned": total}

    def run_due(self, business_id: str | None = None, as_of: datetime | None = None) -> dict:
        now = _utc(as_of)
        due = self.store.due_messages(now)
        if business_id:
            due = [m for m in due if m.business_id == business_id]

        sent = 0
        failed = 0
        for msg in due:
            client = self.store.get_client(msg.client_id)
            biz = self.store.get_business(msg.business_id)
            if not client or not biz:
                self.store.mark_message(msg.id, "failed", "missing client or business")
                failed += 1
                continue
            if client.status in {"recovered", "paused"}:
                self.store.mark_message(msg.id, "skipped", "client not eligible")
                continue

            result = self.sender.send_whatsapp(
                to=client.phone,
                body=msg.body,
                from_number=biz.whatsapp_from,
            )
            if not result.ok:
                # Zimbabwe reality: WhatsApp fails → try SMS once.
                result = self.sender.send_sms(to=client.phone, body=msg.body)

            if result.ok:
                self.store.mark_message(msg.id, "sent")
                self.store.update_client(client.id, status="in_sequence")
                if msg.day >= 90:
                    self.store.update_client(client.id, status="exhausted")
                self.store.add_event(
                    msg.business_id,
                    "message_sent",
                    {
                        "client_id": client.id,
                        "client_name": client.full_name,
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
                {"sent": sent, "failed": failed, "as_of": now.isoformat()},
            )
        return {"sent": sent, "failed": failed, "checked": len(due)}

    def mark_recovered(self, client_id: str) -> Client | None:
        client = self.store.update_client(
            client_id,
            status="recovered",
            recovered_at=datetime.now(timezone.utc).isoformat(),
            last_visit=date.today().isoformat(),
        )
        if client:
            # Skip remaining queued messages.
            for msg in self.store.list_messages(client.business_id, limit=500):
                if msg.client_id == client_id and msg.status == "queued":
                    self.store.mark_message(msg.id, "skipped", "recovered")
            self.store.add_event(
                client.business_id,
                "recovered",
                {"client_id": client.id, "client_name": client.full_name},
            )
        return client

    def preview(self, business_id: str, client_id: str, day: int = 30) -> dict:
        biz = self.store.get_business(business_id)
        client = self.store.get_client(client_id)
        if not biz or not client:
            return {"error": "not found"}
        copy = render_sequence(
            biz.vertical,
            day,
            client_name=client.full_name,
            business_name=biz.name,
            staff_name=client.staff_name or biz.staff_name,
            offer=biz.offer or DEFAULT_OFFERS.get(biz.vertical),
            booking_link=biz.booking_link,
        )
        return {
            "day": copy.day,
            "subject": copy.subject,
            "body": copy.body,
            "channel": "whatsapp",
            "to": client.phone,
        }
