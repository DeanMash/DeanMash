from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from closeloop.db import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    owner_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    login_email: Mapped[str] = mapped_column(String(200), default="", index=True)
    password_hash: Mapped[str] = mapped_column(String(255), default="")
    public_slug: Mapped[str] = mapped_column(String(80), default="", index=True)
    trade_key: Mapped[str] = mapped_column(String(64), default="roofing")
    plan_key: Mapped[str] = mapped_column(String(32), default="growth")
    timezone: Mapped[str] = mapped_column(String(64), default="America/New_York")
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_followup_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    estimates: Mapped[list["Estimate"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )


class Estimate(Base):
    __tablename__ = "estimates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    homeowner_name: Mapped[str] = mapped_column(String(160))
    homeowner_phone: Mapped[str] = mapped_column(String(40), default="")
    homeowner_email: Mapped[str] = mapped_column(String(200), default="")
    address: Mapped[str] = mapped_column(String(255), default="")
    job_title: Mapped[str] = mapped_column(String(200), default="")
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    trade_key: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="open")  # open|won|lost|paused
    lost_reason: Mapped[str] = mapped_column(String(120), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    quoted_on: Mapped[date] = mapped_column(Date, default=date.today)
    next_follow_up_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    business: Mapped[Business] = relationship(back_populates="estimates")
    follow_ups: Mapped[list["FollowUp"]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan", order_by="FollowUp.day"
    )


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estimate_id: Mapped[int] = mapped_column(ForeignKey("estimates.id"), index=True)
    day: Mapped[int] = mapped_column(Integer)  # 0 welcome, 2, 5, or 10
    channel: Mapped[str] = mapped_column(String(32))  # whatsapp|email|call_script|sms
    subject: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    intent: Mapped[str] = mapped_column(String(64), default="")
    scheduled_for: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[str] = mapped_column(Text, default="")

    estimate: Mapped[Estimate] = relationship(back_populates="follow_ups")


class MessageLog(Base):
    __tablename__ = "message_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(Integer, index=True)
    estimate_id: Mapped[int] = mapped_column(Integer, index=True)
    follow_up_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    channel: Mapped[str] = mapped_column(String(32))
    to_address: Mapped[str] = mapped_column(String(255), default="")
    subject: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    provider_status: Mapped[str] = mapped_column(String(64), default="logged")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)