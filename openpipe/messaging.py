"""Outbound email adapters. Demo mode records sends without external APIs."""

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
    """Email sender with demo / stub / live modes."""

    def __init__(self, mode: str | None = None) -> None:
        self.mode = mode or config.EMAIL_MODE

    def send_email(
        self,
        *,
        to: str,
        subject: str,
        body: str,
        from_email: str,
    ) -> SendResult:
        if self.mode == "demo":
            log.info(
                "DEMO Email → %s from %s :: %s | %s",
                to,
                from_email,
                subject,
                body[:80].replace("\n", " "),
            )
            return SendResult(ok=True, channel="email", provider_id=f"demo-em-{to.split('@')[0][:8]}")
        if self.mode == "stub":
            return SendResult(ok=True, channel="email", provider_id="stub")
        return SendResult(
            ok=False,
            channel="email",
            error="Live email not configured. Set OPENPIPE_EMAIL_MODE=demo.",
        )
