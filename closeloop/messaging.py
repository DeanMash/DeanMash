"""Outbound channels — WhatsApp + email (Twilio/SMTP) or durable logs."""

from __future__ import annotations

import base64
import logging
import smtplib
import urllib.parse
import urllib.request
from email.message import EmailMessage

from sqlalchemy.orm import Session

from closeloop.config import Settings, get_settings
from closeloop.models import MessageLog

logger = logging.getLogger(__name__)


def _normalize_whatsapp_address(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if raw.lower().startswith("whatsapp:"):
        return raw
    digits = raw if raw.startswith("+") else f"+{raw}" if raw.isdigit() else raw
    return f"whatsapp:{digits}"


class MessageSender:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _twilio_post(self, payload: dict[str, str]) -> None:
        sid = self.settings.twilio_account_sid
        token = self.settings.twilio_auth_token
        if not (sid and token):
            raise RuntimeError("Twilio credentials missing")
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            data=data,
            method="POST",
        )
        credentials = f"{sid}:{token}".encode()
        req.add_header("Authorization", "Basic " + base64.b64encode(credentials).decode())
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            resp.read()

    def send_sms(self, *, to: str, body: str) -> str:
        if not to:
            return "skipped_no_phone"
        from_number = self.settings.twilio_from_number
        if not (self.settings.twilio_account_sid and self.settings.twilio_auth_token and from_number):
            logger.info("SMS (log-only) → %s: %s", to, body[:120])
            return "logged"
        try:
            self._twilio_post({"To": to, "From": from_number, "Body": body})
            return "sent"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Twilio SMS failed")
            raise RuntimeError(str(exc)) from exc

    def send_whatsapp(self, *, to: str, body: str) -> str:
        if not to:
            return "skipped_no_phone"
        wa_from = self.settings.twilio_whatsapp_from or (
            f"whatsapp:{self.settings.twilio_from_number}"
            if self.settings.twilio_from_number
            else ""
        )
        if not (self.settings.twilio_account_sid and self.settings.twilio_auth_token and wa_from):
            logger.info("WhatsApp (log-only) → %s: %s", to, body[:120])
            return "logged"
        try:
            self._twilio_post(
                {
                    "To": _normalize_whatsapp_address(to),
                    "From": _normalize_whatsapp_address(wa_from),
                    "Body": body,
                }
            )
            return "sent"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Twilio WhatsApp failed")
            raise RuntimeError(str(exc)) from exc

    def send_email(self, *, to: str, subject: str, body: str) -> str:
        if not to:
            return "skipped_no_email"
        host = self.settings.smtp_host
        if not host:
            logger.info("Email (log-only) → %s | %s", to, subject)
            return "logged"
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings.smtp_from
        msg["To"] = to
        msg.set_content(body)
        try:
            with smtplib.SMTP(host, self.settings.smtp_port, timeout=20) as smtp:
                smtp.starttls()
                if self.settings.smtp_user:
                    smtp.login(self.settings.smtp_user, self.settings.smtp_password)
                smtp.send_message(msg)
            return "sent"
        except Exception as exc:  # noqa: BLE001
            logger.exception("SMTP email failed")
            raise RuntimeError(str(exc)) from exc

    def log(
        self,
        db: Session,
        *,
        business_id: int,
        estimate_id: int,
        follow_up_id: int | None,
        channel: str,
        to_address: str,
        subject: str,
        body: str,
        provider_status: str,
    ) -> MessageLog:
        row = MessageLog(
            business_id=business_id,
            estimate_id=estimate_id,
            follow_up_id=follow_up_id,
            channel=channel,
            to_address=to_address,
            subject=subject or "",
            body=body,
            provider_status=provider_status,
        )
        db.add(row)
        return row