"""Verticals where outbound email replaces hated cold calling."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vertical:
    key: str
    label: str
    why: str
    icp: str
    trigger_note: str


VERTICALS: dict[str, Vertical] = {
    "insurance": Vertical(
        key="insurance",
        label="Insurance brokers",
        why="New businesses and growing SMEs need cover — email opens the door without the cold call.",
        icp="SME owners, ops managers, and HR leads at growing local firms",
        trigger_note="Hiring spikes, new premises, fleet additions, tender wins",
    ),
    "advisor": Vertical(
        key="advisor",
        label="Financial advisors",
        why="Busy professionals ignore cold calls; a short personal email earns the first meeting.",
        icp="Business owners, executives, and high-earning professionals",
        trigger_note="Promotions, exits, property purchases, retirement windows",
    ),
    "b2b": Vertical(
        key="b2b",
        label="B2B services",
        why="Agencies and consultancies need a repeatable way to start conversations at scale.",
        icp="Decision-makers at mid-market companies matching your service niche",
        trigger_note="Funding rounds, leadership hires, tech stack changes, expansion",
    ),
    "accounting": Vertical(
        key="accounting",
        label="Accountants & bookkeepers",
        why="Year-end and growth moments create demand — email lands when calls feel pushy.",
        icp="Founders and finance leads at SMEs without a strong accounting partner",
        trigger_note="Company registrations, VAT thresholds, audit season",
    ),
    "consulting": Vertical(
        key="consulting",
        label="Management consultants",
        why="Credibility-first outreach beats dialling; personalised notes show you did the homework.",
        icp="COOs and founders navigating growth, ops, or turnaround pressure",
        trigger_note="Restructuring, new markets, board appointments",
    ),
    "commercial_re": Vertical(
        key="commercial_re",
        label="Commercial real estate",
        why="Lease events and expansion plans are public signals — email arrives before competitors call.",
        icp="Facility managers, founders, and landlords with space needs",
        trigger_note="Lease renewals, office moves, warehouse growth",
    ),
    "recruiting": Vertical(
        key="recruiting",
        label="Recruiters & staffing",
        why="Hiring managers drown in LinkedIn spam; a specific email about their open role stands out.",
        icp="Hiring managers and CHROs with active or seasonal hiring",
        trigger_note="Job posts, team growth announcements, attrition spikes",
    ),
    "legal": Vertical(
        key="legal",
        label="Law firms & attorneys",
        why="Corporate counsel and founders prefer written context before they take a call.",
        icp="General counsel, founders, and ops leads facing compliance or contracts",
        trigger_note="Fundraising, disputes, new jurisdictions, M&A rumour",
    ),
    "it_msp": Vertical(
        key="it_msp",
        label="IT & managed service providers",
        why="Security and uptime fears convert better via clear email than a surprise cold call.",
        icp="IT managers and founders at firms with aging stacks or no MSP",
        trigger_note="Outages in the news, cloud migrations, compliance deadlines",
    ),
    "agency": Vertical(
        key="agency",
        label="Marketing & creative agencies",
        why="Prospects ignore pitch decks on the phone — a sharp email about their brand wins the reply.",
        icp="CMOs and founders whose brand looks stale or underinvested",
        trigger_note="Rebrands, product launches, competitor campaigns",
    ),
}


def list_verticals() -> list[Vertical]:
    return list(VERTICALS.values())


def get_vertical(key: str) -> Vertical:
    return VERTICALS.get(key, VERTICALS["insurance"])
