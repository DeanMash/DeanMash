"""Outbound channel adapters. Demo mode records sends without external APIs."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from . import config

log = logging.getLogger("comehome.messaging")


@dataclass
class SendResult:
    ok: bool
    channel: str
    provider_id: str | None = None
    error: str | None = None


class MessageSender:
    """WhatsApp-first sender with SMS fallback stub for Zimbabwe networks."""

    def __init__(self, mode: str | None = None) -> None:
        self.mode = mode or config.WHATSAPP_MODE

    def send_whatsapp(self, *, to: str, body: str, from_number: str) -> SendResult:
        if self.mode == "demo":
            log.info("DEMO WhatsApp → %s from %s :: %s", to, from_number, body[:80])
            return SendResult(ok=True, channel="whatsapp", provider_id=f"demo-wa-{to[-4:]}")
        if self.mode == "stub":
            return SendResult(ok=True, channel="whatsapp", provider_id="stub")
        # Live mode intentionally not implemented without credentials.
        return SendResult(
            ok=False,
            channel="whatsapp",
            error="Live WhatsApp not configured. Set COMEHOME_WHATSAPP_MODE=demo.",
        )

    def send_sms(self, *, to: str, body: str) -> SendResult:
        if self.mode in {"demo", "stub"}:
            log.info("DEMO SMS → %s :: %s", to, body[:80])
            return SendResult(ok=True, channel="sms", provider_id=f"demo-sms-{to[-4:]}")
        return SendResult(ok=False, channel="sms", error="Live SMS not configured")
