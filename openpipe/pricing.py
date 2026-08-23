"""Monthly plans — done-for-you outbound email for brokers, advisors, and B2B."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Plan:
    key: str
    name: str
    price_usd: int
    tagline: str
    prospects: str
    features: list[str]
    best_for: str


PLANS: list[Plan] = [
    Plan(
        key="starter",
        name="Starter",
        price_usd=900,
        tagline="Register your firm. Personalised email + WhatsApp that gets replies.",
        prospects="Up to 500 new prospects / month",
        features=[
            "Self-serve org registration + private access token",
            "Prospect discovery by niche + city",
            "Day 0 / 3 / 7 email + WhatsApp sequences",
            "Trigger-signal personalisation",
            "Auto-send due messages (demo or live)",
        ],
        best_for="Solo brokers, advisors, and boutique B2B firms",
    ),
    Plan(
        key="pipeline",
        name="Pipeline",
        price_usd=1500,
        tagline="Fill more meetings without the cold-call list — email and WhatsApp.",
        prospects="Up to 2,000 new prospects / month",
        features=[
            "Everything in Starter",
            "Multi-offer sequences per vertical",
            "Channel mix: email, WhatsApp, or both",
            "Priority copy review before send waves",
            "Monthly pipeline strategy call",
        ],
        best_for="Growing brokerages, advisory practices, agencies",
    ),
    Plan(
        key="scale",
        name="Scale",
        price_usd=2500,
        tagline="Multi-seat outbound on one email + WhatsApp system.",
        prospects="Up to 5,000 new prospects / month",
        features=[
            "Everything in Pipeline",
            "Up to 5 sender seats / brands",
            "Shared + seat-specific sequences",
            "Dedicated success manager",
            "CRM / CSV import assistance",
        ],
        best_for="Multi-advisor firms, broker networks, B2B teams",
    ),
]


def list_plans() -> list[dict]:
    return [asdict(p) for p in PLANS]


def get_plan(key: str) -> Plan:
    for plan in PLANS:
        if plan.key == key:
            return plan
    return PLANS[0]
