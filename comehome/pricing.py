"""Monthly plans — premium done-for-you win-back for high-LTV service businesses."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Plan:
    key: str
    name: str
    price_usd: int
    tagline: str
    clients: str
    features: list[str]
    best_for: str


PLANS: list[Plan] = [
    Plan(
        key="studio",
        name="Studio",
        price_usd=800,
        tagline="One location, full cadence, WhatsApp-first.",
        clients="Up to 400 active clients",
        features=[
            "30 / 60 / 90 personal message sequences",
            "WhatsApp + SMS fallback",
            "Vertical-tuned copy (gym, clinic, spa…)",
            "Weekly recovery report",
            "Harare / Bulawayo onboarding call",
        ],
        best_for="Single gym, salon, spa, or solo practitioner",
    ),
    Plan(
        key="practice",
        name="Practice",
        price_usd=1400,
        tagline="Busier books, more seats recovered.",
        clients="Up to 1,200 active clients",
        features=[
            "Everything in Studio",
            "Multi-staff personalization",
            "Custom offers per sequence step",
            "Priority message review",
            "Monthly strategy call",
        ],
        best_for="Growing clinics, popular salons, mid-size gyms",
    ),
    Plan(
        key="chain",
        name="Chain",
        price_usd=2000,
        tagline="Multi-branch retention on one system.",
        clients="Up to 3,000 active clients",
        features=[
            "Everything in Practice",
            "Up to 5 branches / brands",
            "Shared + location-specific sequences",
            "Dedicated success manager",
            "CSV / POS import assistance",
        ],
        best_for="Multi-branch fitness, dental groups, beauty chains",
    ),
]


def list_plans() -> list[dict]:
    return [asdict(p) for p in PLANS]


def get_plan(key: str) -> Plan:
    for plan in PLANS:
        if plan.key == key:
            return plan
    return PLANS[0]
