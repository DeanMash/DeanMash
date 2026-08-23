"""Channel plans: email, WhatsApp, or both for Day 0 / 3 / 7."""

from __future__ import annotations

CHANNEL_CHOICES = ("email", "whatsapp", "both")


def normalize_channels(value: str | None) -> str:
    raw = (value or "both").strip().lower()
    if raw in CHANNEL_CHOICES:
        return raw
    if raw in {"wa", "whatsapp_only"}:
        return "whatsapp"
    if raw in {"mail", "email_only"}:
        return "email"
    return "both"


def channels_for_day(biz_channels: str, day: int, *, has_phone: bool) -> list[str]:
    """
    Pick outbound channel(s) for a sequence day.

    both:
      Day 0 → email (longer first touch)
      Day 3 → WhatsApp bump (email if no phone)
      Day 7 → email + WhatsApp soft close (WhatsApp only if phone)
    """
    mode = normalize_channels(biz_channels)
    if mode == "email":
        return ["email"]
    if mode == "whatsapp":
        return ["whatsapp"] if has_phone else ["email"]
    # both
    if day == 0:
        return ["email"]
    if day == 3:
        return ["whatsapp"] if has_phone else ["email"]
    if day >= 7:
        out = ["email"]
        if has_phone:
            out.append("whatsapp")
        return out
    return ["email"]
