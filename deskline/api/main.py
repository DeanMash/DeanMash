"""Deskline qualification + booking API (demo companion).

Run from repo root (with FastAPI already installed):

    uvicorn deskline.api.main:app --reload --port 8010

Or:

    cd deskline && uvicorn api.main:app --reload --port 8010
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

IndustryId = Literal["dental", "plumber", "medspa"]

INDUSTRIES = {
    "dental": {
        "name": "Dental surgeries",
        "working_hours": {"start": 9, "end": 17, "days": [0, 1, 2, 3, 4]},
        "slot_minutes": 30,
        "greeting": (
            "Thanks for calling. You’ve reached our after-hours desk. "
            "I’m Deskline — I can help book the next available appointment."
        ),
    },
    "plumber": {
        "name": "Plumbers",
        "working_hours": {"start": 8, "end": 17, "days": [0, 1, 2, 3, 4, 5]},
        "slot_minutes": 60,
        "greeting": (
            "You’ve reached us after hours. I’m Deskline — "
            "I can take job details and book the next engineer visit."
        ),
    },
    "medspa": {
        "name": "Med spas",
        "working_hours": {"start": 10, "end": 18, "days": [1, 2, 3, 4, 5]},
        "slot_minutes": 45,
        "greeting": (
            "Our studio is closed, but I’m Deskline — "
            "I can reserve a consult for the next open day."
        ),
    },
}


class QualifyRequest(BaseModel):
    industry: IndustryId
    answers: dict[str, str] = Field(default_factory=dict)
    score_hint: int | None = None
    urgent: bool = False


class Slot(BaseModel):
    id: str
    label: str
    day_label: str
    start_iso: str


class QualifyResponse(BaseModel):
    status: Literal["qualified", "triage", "callback"]
    score: int
    urgent: bool
    message: str
    recommended_slot: Slot | None
    slots: list[Slot]


class BookRequest(BaseModel):
    industry: IndustryId
    caller_name: str
    phone: str
    slot_id: str
    service: str | None = None


app = FastAPI(title="Deskline API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOOKINGS: list[dict] = []


def _next_working_day(industry: IndustryId, from_dt: datetime) -> datetime:
    cfg = INDUSTRIES[industry]["working_hours"]
    cursor = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    hour = from_dt.hour + from_dt.minute / 60
    if hour >= cfg["end"]:
        cursor += timedelta(days=1)
    for _ in range(14):
        # Python weekday: Mon=0 … Sun=6 (matches our config)
        if cursor.weekday() in cfg["days"]:
            return cursor
        cursor += timedelta(days=1)
    return cursor


def _build_slots(industry: IndustryId, from_dt: datetime | None = None, count: int = 6) -> list[Slot]:
    now = from_dt or datetime.now()
    cfg = INDUSTRIES[industry]
    hours = cfg["working_hours"]
    day = _next_working_day(industry, now)
    slots: list[Slot] = []
    step = cfg["slot_minutes"] / 60
    hour = float(hours["start"])
    while hour < hours["end"] and len(slots) < count:
        whole = int(hour)
        minutes = int(round((hour - whole) * 60))
        start = day.replace(hour=whole, minute=minutes, second=0, microsecond=0)
        label = start.strftime("%I:%M %p").lstrip("0")
        day_label = start.strftime("%a, %b ") + str(start.day)
        slots.append(
            Slot(
                id=start.isoformat(),
                label=label,
                day_label=day_label,
                start_iso=start.isoformat(),
            )
        )

        hour += step
    return slots


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "deskline"}


@app.get("/industries")
def list_industries() -> dict:
    return {
        key: {
            "id": key,
            "name": value["name"],
            "greeting": value["greeting"],
            "working_hours": value["working_hours"],
            "slot_minutes": value["slot_minutes"],
        }
        for key, value in INDUSTRIES.items()
    }


@app.get("/slots/{industry}", response_model=list[Slot])
def get_slots(industry: IndustryId) -> list[Slot]:
    if industry not in INDUSTRIES:
        raise HTTPException(status_code=404, detail="Unknown industry")
    return _build_slots(industry)


@app.post("/qualify", response_model=QualifyResponse)
def qualify(payload: QualifyRequest) -> QualifyResponse:
    # Lightweight server-side scoring for telephony webhooks.
    base = payload.score_hint if payload.score_hint is not None else 40
    urgent_keys = {"pain", "flood", "boiler", "break", "event"}
    urgent = payload.urgent or any(v in urgent_keys for v in payload.answers.values())
    score = min(100, base + (25 if urgent else 0) + len(payload.answers) * 5)
    slots = _build_slots(payload.industry)

    if urgent or score >= 70:
        status: Literal["qualified", "triage", "callback"] = "triage"
        message = "Urgent lead flagged — priority working-hours slot offered."
        recommended = slots[0] if slots else None
    elif score >= 45:
        status = "qualified"
        message = "Lead qualified — appointment held for next working day."
        recommended = slots[min(2, len(slots) - 1)] if slots else None
    else:
        status = "callback"
        message = "Soft lead captured — practice notified for a warm callback."
        recommended = None

    return QualifyResponse(
        status=status,
        score=score,
        urgent=urgent,
        message=message,
        recommended_slot=recommended,
        slots=slots,
    )


@app.post("/book")
def book(payload: BookRequest) -> dict:
    slots = _build_slots(payload.industry)
    slot = next((item for item in slots if item.id == payload.slot_id), None)
    if slot is None:
        raise HTTPException(status_code=400, detail="Slot unavailable")
    record = {
        "id": f"bk_{len(BOOKINGS) + 1}",
        "industry": payload.industry,
        "caller_name": payload.caller_name,
        "phone": payload.phone,
        "service": payload.service,
        "slot": slot.model_dump(),
        "created_at": datetime.now().isoformat(),
    }
    BOOKINGS.append(record)
    return {"ok": True, "booking": record}


@app.get("/bookings")
def list_bookings() -> list[dict]:
    return BOOKINGS
