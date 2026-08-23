"""ICP starter kits — insurance, advisors, B2B (the OpenPipe core)."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class StarterKit:
    id: str
    name: str
    vertical: str
    city: str
    sender_name: str
    sender_email: str
    booking_link: str
    offer: str
    plan: str
    niche: str
    blurb: str
    start_tip: str


# Fixed IDs so the operator dashboard can switch demos reliably.
STARTERS: list[StarterKit] = [
    StarterKit(
        id="demo-insurance",
        name="Horizon Cover Brokers",
        vertical="insurance",
        city="Harare",
        sender_name="Tariro Moyo",
        sender_email="tariro@horizoncover.example",
        booking_link="https://cal.example/horizon-cover",
        offer="a 20-minute cover gap review for your business",
        plan="pipeline",
        niche="fleet logistics sme",
        blurb="Find growing SMEs with fleet, site, or headcount triggers — then open with cover-gap email.",
        start_tip="Start with fleet / logistics owners who just expanded.",
    ),
    StarterKit(
        id="demo-advisor",
        name="Summit Wealth Advisors",
        vertical="advisor",
        city="Harare",
        sender_name="Rutendo Chari",
        sender_email="rutendo@summitwealth.example",
        booking_link="https://cal.example/summit-wealth",
        offer="a no-obligation wealth & risk snapshot",
        plan="pipeline",
        niche="executive funding wealth",
        blurb="Reach founders and executives at life moments — funding, promotion, exit — via short personal email.",
        start_tip="Start with executives after funding or role changes.",
    ),
    StarterKit(
        id="demo-b2b",
        name="Northline Growth",
        vertical="b2b",
        city="Harare",
        sender_name="Farai Ncube",
        sender_email="farai@northline.example",
        booking_link="https://cal.example/northline",
        offer="a short diagnostic on where your pipeline is leaking",
        plan="pipeline",
        niche="saas agency outbound growth",
        blurb="Fill meetings for B2B services with trigger-aware Day 0 / 3 / 7 sequences — no cold-call list.",
        start_tip="Start with growth leads whose pipeline still depends on manual outreach.",
    ),
]


# Sample prospect context for marketing-site email previews (per vertical).
SAMPLE_PROSPECTS: dict[str, dict[str, str]] = {
    "insurance": {
        "prospect_name": "Tendai Chirwa",
        "company": "BrightPath Logistics",
        "title": "Managing Director",
        "trigger": "Just added 8 delivery vans after a retail contract win",
        "sender_name": "Tariro Moyo",
        "business_name": "Horizon Cover Brokers",
    },
    "advisor": {
        "prospect_name": "Kudzai Williams",
        "company": "FinLedge Holdings",
        "title": "CFO",
        "trigger": "Preparing Series A; personal and corporate planning in flux",
        "sender_name": "Rutendo Chari",
        "business_name": "Summit Wealth Advisors",
    },
    "b2b": {
        "prospect_name": "Precious Dube",
        "company": "GrowthStack Africa",
        "title": "VP Sales",
        "trigger": "Building an outbound motion for mid-market SaaS buyers",
        "sender_name": "Farai Ncube",
        "business_name": "Northline Growth",
    },
}


CORE_VERTICALS = ("insurance", "advisor", "b2b")


def list_starters() -> list[dict]:
    return [asdict(s) for s in STARTERS]


def get_starter(vertical: str) -> StarterKit:
    for s in STARTERS:
        if s.vertical == vertical or s.id == vertical:
            return s
    return STARTERS[0]
