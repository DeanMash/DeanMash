from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from closeloop.auth import hash_password, new_public_slug, verify_password
from closeloop.messaging import MessageSender
from closeloop.models import Business, Estimate, FollowUp, MessageLog
from closeloop.trades import FOLLOW_UP_DAYS, PRICING_TIERS, get_trade, list_trades

AUTO_CHANNELS = ("whatsapp", "email", "sms")


def _first_name(full_name: str) -> str:
    parts = (full_name or "").strip().split()
    return parts[0] if parts else "there"


def _money(amount: float) -> str:
    return f"{amount:,.0f}" if amount >= 100 else f"{amount:,.2f}"


def render_template(template: str, ctx: dict[str, str]) -> str:
    out = template
    for key, value in ctx.items():
        out = out.replace("{" + key + "}", value)
    return out


def build_context(business: Business, estimate: Estimate) -> dict[str, str]:
    return {
        "homeowner_first": _first_name(estimate.homeowner_name),
        "homeowner_name": estimate.homeowner_name,
        "company": business.name,
        "owner_name": business.owner_name,
        "company_phone": business.phone or "us",
        "address": estimate.address or "your property",
        "estimate_amount": _money(estimate.amount),
        "job_title": estimate.job_title or "the project",
    }


def next_follow_up_date(quoted_on: date, today: date | None = None) -> date | None:
    today = today or date.today()
    for day in FOLLOW_UP_DAYS:
        candidate = quoted_on + timedelta(days=day)
        if candidate >= today:
            return candidate
    return None


def _welcome_copies(ctx: dict[str, str]) -> list[tuple[str, str, str, str]]:
    """Immediate Day-0 confirmations (channel, subject, body, intent)."""
    wa = (
        "Hi {homeowner_first}, thanks for meeting {company}. Your estimate for "
        "{address} (${estimate_amount}) is in — we’ll follow up so nothing falls "
        "through the cracks. — {owner_name}"
    )
    email_body = (
        "Hi {homeowner_first},\n\n"
        "Thank you for having {company} out. Your estimate for {address} is "
        "${estimate_amount}.\n\n"
        "We’ll check in over the next 10 days on WhatsApp and email in case you "
        "have questions. You can also reach {owner_name} at {company_phone}.\n\n"
        "— {owner_name}\n{company}"
    )
    return [
        ("whatsapp", "", render_template(wa, ctx), "welcome"),
        (
            "email",
            render_template("Thanks for the visit — estimate for {address}", ctx),
            render_template(email_body, ctx),
            "welcome",
        ),
    ]


def schedule_follow_ups(db: Session, business: Business, estimate: Estimate) -> list[FollowUp]:
    trade_key = estimate.trade_key or business.trade_key
    trade = get_trade(trade_key)
    ctx = build_context(business, estimate)
    created: list[FollowUp] = []

    # Day 0 welcome — due immediately so automatic outreach starts as soon as
    # the contractor saves the client.
    for channel, subject, body, intent in _welcome_copies(ctx):
        if channel == "whatsapp" and not business.whatsapp_enabled:
            continue
        if channel == "email" and not business.email_followup_enabled:
            continue
        row = FollowUp(
            estimate_id=estimate.id,
            day=0,
            channel=channel,
            subject=subject,
            body=body,
            intent=intent,
            scheduled_for=estimate.quoted_on,
            status="pending",
        )
        db.add(row)
        created.append(row)

    for copy in trade.sequences:
        if copy.channel == "whatsapp" and not business.whatsapp_enabled:
            continue
        if copy.channel == "email" and not business.email_followup_enabled:
            continue
        row = FollowUp(
            estimate_id=estimate.id,
            day=copy.day,
            channel=copy.channel,
            subject=render_template(copy.subject or "", ctx),
            body=render_template(copy.body, ctx),
            intent=copy.intent,
            scheduled_for=estimate.quoted_on + timedelta(days=copy.day),
            status="pending",
        )
        db.add(row)
        created.append(row)
    estimate.next_follow_up_on = next_follow_up_date(estimate.quoted_on)
    db.flush()
    return created


def create_business(
    db: Session,
    *,
    name: str,
    owner_name: str,
    phone: str = "",
    email: str = "",
    login_email: str = "",
    password: str = "",
    trade_key: str = "roofing",
    plan_key: str = "growth",
) -> Business:
    get_trade(trade_key)  # validate
    login = (login_email or email).strip().lower()
    if login:
        existing = get_business_by_login(db, login)
        if existing:
            raise ValueError("An account with that email already exists. Please log in.")
    biz = Business(
        name=name.strip(),
        owner_name=owner_name.strip(),
        phone=phone.strip(),
        email=email.strip() or login,
        login_email=login,
        password_hash=hash_password(password) if password else "",
        public_slug=new_public_slug(name),
        trade_key=trade_key,
        plan_key=plan_key,
        whatsapp_enabled=True,
        email_followup_enabled=True,
    )
    db.add(biz)
    db.commit()
    db.refresh(biz)
    return biz


def authenticate_business(db: Session, login_email: str, password: str) -> Business | None:
    biz = get_business_by_login(db, login_email.strip().lower())
    if not biz or not biz.password_hash:
        return None
    if not verify_password(password, biz.password_hash):
        return None
    return biz


def get_business_by_login(db: Session, login_email: str) -> Business | None:
    return db.scalar(
        select(Business).where(Business.login_email == login_email.strip().lower()).limit(1)
    )


def get_business_by_id(db: Session, business_id: int) -> Business | None:
    return db.get(Business, business_id)


def create_estimate(
    db: Session,
    business: Business,
    *,
    homeowner_name: str,
    homeowner_phone: str = "",
    homeowner_email: str = "",
    address: str = "",
    job_title: str = "",
    amount: float = 0.0,
    trade_key: str | None = None,
    quoted_on: date | None = None,
    notes: str = "",
    sender: MessageSender | None = None,
    send_due_now: bool = True,
) -> Estimate:
    estimate = Estimate(
        business_id=business.id,
        homeowner_name=homeowner_name.strip(),
        homeowner_phone=homeowner_phone.strip(),
        homeowner_email=homeowner_email.strip(),
        address=address.strip(),
        job_title=job_title.strip(),
        amount=float(amount or 0),
        trade_key=(trade_key or business.trade_key),
        quoted_on=quoted_on or date.today(),
        notes=notes.strip(),
        status="open",
    )
    db.add(estimate)
    db.flush()
    schedule_follow_ups(db, business, estimate)
    db.commit()
    db.refresh(estimate)

    # Fire any follow-ups already due (Day 0 welcome + late-entered quotes).
    if send_due_now:
        process_due_follow_ups(
            db,
            on_day=date.today(),
            sender=sender or MessageSender(),
            estimate_id=estimate.id,
        )
        db.refresh(estimate)
    return estimate


def set_estimate_status(
    db: Session,
    estimate: Estimate,
    status: str,
    lost_reason: str = "",
) -> Estimate:
    if status not in {"open", "won", "lost", "paused"}:
        raise ValueError("Invalid status")
    estimate.status = status
    estimate.lost_reason = lost_reason if status == "lost" else ""
    if status in {"won", "lost"}:
        for fu in estimate.follow_ups:
            if fu.status == "pending":
                fu.status = "skipped"
        estimate.next_follow_up_on = None
    elif status == "paused":
        estimate.next_follow_up_on = None
    else:
        estimate.next_follow_up_on = next_follow_up_date(estimate.quoted_on)
        for fu in estimate.follow_ups:
            if fu.status == "skipped" and fu.scheduled_for >= date.today():
                fu.status = "pending"
    db.commit()
    db.refresh(estimate)
    return estimate


def due_follow_ups(
    db: Session,
    on_day: date | None = None,
    *,
    estimate_id: int | None = None,
) -> list[FollowUp]:
    on_day = on_day or date.today()
    stmt: Select[tuple[FollowUp]] = (
        select(FollowUp)
        .options(joinedload(FollowUp.estimate).joinedload(Estimate.business))
        .join(Estimate)
        .where(
            FollowUp.status == "pending",
            FollowUp.scheduled_for <= on_day,
            Estimate.status == "open",
            FollowUp.channel.in_(AUTO_CHANNELS),
        )
        .order_by(FollowUp.scheduled_for, FollowUp.id)
    )
    if estimate_id is not None:
        stmt = stmt.where(FollowUp.estimate_id == estimate_id)
    return list(db.scalars(stmt).unique())


def process_due_follow_ups(
    db: Session,
    *,
    on_day: date | None = None,
    sender: MessageSender | None = None,
    estimate_id: int | None = None,
) -> dict[str, int]:
    sender = sender or MessageSender()
    due = due_follow_ups(db, on_day, estimate_id=estimate_id)
    stats = {"processed": 0, "sent": 0, "failed": 0, "skipped": 0}
    for fu in due:
        estimate = fu.estimate
        business = estimate.business
        stats["processed"] += 1
        try:
            if fu.channel == "whatsapp":
                status = sender.send_whatsapp(to=estimate.homeowner_phone, body=fu.body)
                to_addr = estimate.homeowner_phone
            elif fu.channel == "sms":
                status = sender.send_sms(to=estimate.homeowner_phone, body=fu.body)
                to_addr = estimate.homeowner_phone
            else:
                status = sender.send_email(
                    to=estimate.homeowner_email,
                    subject=fu.subject or f"Follow-up from {business.name}",
                    body=fu.body,
                )
                to_addr = estimate.homeowner_email
            if status.startswith("skipped"):
                fu.status = "skipped"
                stats["skipped"] += 1
            else:
                fu.status = "sent"
                fu.sent_at = datetime.utcnow()
                stats["sent"] += 1
            sender.log(
                db,
                business_id=business.id,
                estimate_id=estimate.id,
                follow_up_id=fu.id,
                channel=fu.channel,
                to_address=to_addr,
                subject=fu.subject,
                body=fu.body,
                provider_status=status,
            )
        except Exception as exc:  # noqa: BLE001
            fu.status = "failed"
            fu.error = str(exc)
            stats["failed"] += 1
            sender.log(
                db,
                business_id=business.id,
                estimate_id=estimate.id,
                follow_up_id=fu.id,
                channel=fu.channel,
                to_address=estimate.homeowner_phone or estimate.homeowner_email,
                subject=fu.subject,
                body=fu.body,
                provider_status="failed",
            )
        estimate.next_follow_up_on = next_follow_up_date(estimate.quoted_on, on_day or date.today())
    db.commit()
    return stats


def pipeline_stats(db: Session, business_id: int) -> dict[str, Any]:
    estimates = list(
        db.scalars(select(Estimate).where(Estimate.business_id == business_id)).all()
    )
    open_ests = [e for e in estimates if e.status == "open"]
    won = [e for e in estimates if e.status == "won"]
    lost = [e for e in estimates if e.status == "lost"]
    open_value = sum(e.amount for e in open_ests)
    won_value = sum(e.amount for e in won)
    decided = len(won) + len(lost)
    close_rate = (len(won) / decided * 100) if decided else 0.0
    today = date.today()
    due_today = db.scalar(
        select(func.count(FollowUp.id))
        .join(Estimate)
        .where(
            Estimate.business_id == business_id,
            Estimate.status == "open",
            FollowUp.status == "pending",
            FollowUp.scheduled_for <= today,
            FollowUp.channel.in_(AUTO_CHANNELS),
        )
    )
    calls_due = db.scalar(
        select(func.count(FollowUp.id))
        .join(Estimate)
        .where(
            Estimate.business_id == business_id,
            Estimate.status == "open",
            FollowUp.status == "pending",
            FollowUp.scheduled_for <= today,
            FollowUp.channel == "call_script",
        )
    )
    return {
        "open_count": len(open_ests),
        "won_count": len(won),
        "lost_count": len(lost),
        "open_value": open_value,
        "won_value": won_value,
        "close_rate": close_rate,
        "due_today": int(due_today or 0),
        "calls_due": int(calls_due or 0),
    }


def get_default_business(db: Session) -> Business | None:
    return db.scalar(select(Business).order_by(Business.id).limit(1))


def list_estimates(db: Session, business_id: int, status: str | None = None) -> list[Estimate]:
    stmt = (
        select(Estimate)
        .options(joinedload(Estimate.follow_ups))
        .where(Estimate.business_id == business_id)
        .order_by(Estimate.quoted_on.desc(), Estimate.id.desc())
    )
    if status:
        stmt = stmt.where(Estimate.status == status)
    return list(db.scalars(stmt).unique())


def recent_messages(db: Session, business_id: int, limit: int = 20) -> list[MessageLog]:
    stmt = (
        select(MessageLog)
        .where(MessageLog.business_id == business_id)
        .order_by(MessageLog.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def pricing_tiers() -> list[dict[str, Any]]:
    return list(PRICING_TIERS)


def trade_catalog() -> list[dict[str, str]]:
    return [
        {
            "key": t.key,
            "label": t.label,
            "emoji": t.emoji,
            "avg_ticket": t.avg_ticket,
            "pain_point": t.pain_point,
        }
        for t in list_trades()
    ]