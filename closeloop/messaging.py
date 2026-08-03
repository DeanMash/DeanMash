"""Outbound channels — Twilio/SMTP when configured, otherwise durable logs."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from closeloop.config import Settings, get_settings
from closeloop.models import MessageLog

logger = logging.getLogger(__name__)


class MessageSender:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def send_sms(self, *, to: str, body: str) -> str:
        if not to:
            return "skipped_no_phone"
        sid = self.settings.twilio_account_sid
        token = self.settings.twilio_auth_token
        from_number = self.settings.twilio_from_number
        if not (sid and token and from_number):
            logger.info("SMS (log-only) → %s: %s", to, body[:120])
            return "logged"
        try:
            import urllib.parse
            import urllib.request

            data = urllib.parse.urlencode(
                {"To": to, "From": from_number, "Body": body}
            ).encode()
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                data=data,
                method="POST",
            )
            credentials = f"{sid}:{token}".encode()
            import base64

            req.add_header("Authorization", "Basic " + base64.b64encode(credentials).decode())
            with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
                resp.read()
            return "sent"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Twilio SMS failed")
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