"""Outbound email + WhatsApp adapters. Demo mode records sends without external APIs."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from . import config

log = logging.getLogger("openpipe.messaging")


@dataclass
class SendResult:
    ok: bool
    channel: str
    provider_id: str | None = None
    error: str | None = None


class MessageSender:
    """Email + WhatsApp sender with demo / stub / live modes."""

    def __init__(self, mode: str | None = None) -> None:
        self.mode = mode or config.EMAIL_MODE

    def send(
        self,
        *,
        channel: str,
        to: str,
        subject: str,
        body: str,
        from_email: str = "",
        from_whatsapp: str = "",
    ) -> SendResult:
        if channel == "whatsapp":
            return self.send_whatsapp(to=to, body=body, from_number=from_whatsapp)
        return self.send_email(
            to=to, subject=subject, body=body, from_email=from_email
        )

    def send_email(
        self,
        *,
        to: str,
        subject: str,
        body: str,
        from_email: str,
    ) -> SendResult:
        if not to or "@" not in to:
            return SendResult(ok=False, channel="email", error="Missing prospect email")
        if self.mode == "demo":
            log.info(
                "DEMO Email → %s from %s :: %s | %s",
                to,
                from_email,
                subject,
                body[:80].replace("\n", " "),
            )
            return SendResult(
                ok=True,
                channel="email",
                provider_id=f"demo-em-{(to.split('@')[0])[:8]}",
            )
        if self.mode == "stub":
            return SendResult(ok=True, channel="email", provider_id="stub")
        return SendResult(
            ok=False,
            channel="email",
            error="Live email not configured. Set OPENPIPE_EMAIL_MODE=demo.",
        )

    def send_whatsapp(
        self,
        *,
        to: str,
        body: str,
        from_number: str = "",
    ) -> SendResult:
        phone = (to or "").strip()
        if not phone:
            return SendResult(
                ok=False, channel="whatsapp", error="Missing prospect WhatsApp number"
            )
        if self.mode == "demo":
            log.info(
                "DEMO WhatsApp → %s from %s :: %s",
                phone,
                from_number or "openpipe-demo",
                body[:100].replace("\n", " "),
            )
            return SendResult(
                ok=True,
                channel="whatsapp",
                provider_id=f"demo-wa-{phone[-6:]}",
            )
        if self.mode == "stub":
            return SendResult(ok=True, channel="whatsapp", provider_id="stub")
        return SendResult(
            ok=False,
            channel="whatsapp",
            error="Live WhatsApp not configured. Set OPENPIPE_EMAIL_MODE=demo.",
        )
