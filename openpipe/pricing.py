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
        tagline="One book of business, personalised email that actually gets replies.",
        prospects="Up to 500 new prospects / month",
        features=[
            "Prospect discovery by niche + city",
            "Day 0 / 3 / 7 personalised email sequences",
            "Vertical-tuned copy (insurance, advisors, B2B…)",
            "Weekly reply & pipeline report",
            "Onboarding call for your ICP",
        ],
        best_for="Solo brokers, advisors, and boutique B2B firms",
    ),
    Plan(
        key="pipeline",
        name="Pipeline",
        price_usd=1500,
        tagline="Fill more meetings without picking up the cold-call list.",
        prospects="Up to 2,000 new prospects / month",
        features=[
            "Everything in Starter",
            "Multi-offer sequences per vertical",
            "Trigger-signal research notes in each email",
            "Priority copy review before send waves",
            "Monthly pipeline strategy call",
        ],
        best_for="Growing brokerages, advisory practices, agencies",
    ),
    Plan(
        key="scale",
        name="Scale",
        price_usd=2500,
        tagline="Multi-seat outbound on one system.",
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
