"""Personalised cold-email sequences — Day 0 / 3 / 7."""

from __future__ import annotations

from dataclasses import dataclass

SEQUENCE_DAYS = (0, 3, 7)

DEFAULT_OFFERS: dict[str, str] = {
    "insurance": "a 20-minute cover gap review for your business",
    "advisor": "a no-obligation wealth & risk snapshot",
    "b2b": "a short diagnostic on where your pipeline is leaking",
    "accounting": "a free books health check before tax season",
    "consulting": "a 30-minute ops bottleneck review",
    "commercial_re": "a space-needs brief matched to live inventory",
    "recruiting": "a shortlist of three candidates for your open role",
    "legal": "a 15-minute risk scan on your next transaction",
    "it_msp": "a no-cost infrastructure resilience check",
    "agency": "a brand & funnel teardown with three concrete fixes",
}


@dataclass(frozen=True)
class EmailCopy:
    day: int
    subject: str
    body: str


def first_name(full_name: str) -> str:
    return (full_name or "there").strip().split()[0]


def all_days() -> tuple[int, ...]:
    return SEQUENCE_DAYS


def render_sequence(
    vertical: str,
    day: int,
    *,
    prospect_name: str,
    company: str,
    title: str,
    trigger: str,
    sender_name: str,
    business_name: str,
    offer: str | None = None,
    booking_link: str = "https://openpipe.example/book",
) -> EmailCopy:
    offer_text = offer or DEFAULT_OFFERS.get(vertical, DEFAULT_OFFERS["b2b"])
    name = first_name(prospect_name)
    templates = _TEMPLATES.get(vertical, _TEMPLATES["b2b"])
    day_key = day if day in templates else 0
    subject_tpl, body_tpl = templates[day_key]
    ctx = {
        "name": name,
        "full_name": prospect_name,
        "company": company,
        "title": title,
        "trigger": trigger,
        "sender": sender_name,
        "business": business_name,
        "offer": offer_text,
        "link": booking_link,
    }
    return EmailCopy(
        day=day_key,
        subject=subject_tpl.format(**ctx),
        body=body_tpl.format(**ctx).strip(),
    )


# Subject + body templates per vertical and sequence day.
_TEMPLATES: dict[str, dict[int, tuple[str, str]]] = {
    "insurance": {
        0: (
            "Quick thought for {company}",
            """Hi {name},

I noticed {trigger} — congratulations. Growth like that usually creates cover gaps (fleet, liability, staff) that only show up when something goes wrong.

I'm {sender} at {business}. We help businesses like {company} close those gaps without a hard sell.

Would {offer} be useful this week?

{sender}
{business}
Book a slot: {link}""",
        ),
        3: (
            "Cover gaps at {company}?",
            """Hi {name},

Following up briefly. When firms expand (new sites, vans, hires), the policy they bought last year often lags reality.

Happy to send a one-page checklist you can run internally — or do {offer} together.

Either way works for me.

{sender}""",
        ),
        7: (
            "Worth 20 minutes, {name}?",
            """Hi {name},

I'll keep this short — if cover for {company} is already sorted, ignore this.

If not, {offer} is open this week: {link}

{sender}
{business}""",
        ),
    },
    "advisor": {
        0: (
            "{name} — timing question",
            """Hi {name},

{trigger} usually means cash-flow, tax, and personal planning shift at the same time. Most executives wait until year-end; a few get ahead of it.

I'm {sender} with {business}. I work with people in roles like {title} at companies such as {company}.

Open to {offer}?

{sender}
{link}""",
        ),
        3: (
            "One page for {company}",
            """Hi {name},

I put together a short snapshot framework we use with founders/executives after moments like yours ({trigger}).

If useful, I can walk you through it in 20 minutes — {offer}.

{sender}""",
        ),
        7: (
            "Close the loop?",
            """Hi {name},

No pressure — if now isn't the right window at {company}, I'll step back.

If it is, here's a link for {offer}: {link}

{sender}
{business}""",
        ),
    },
    "b2b": {
        0: (
            "Idea for {company}'s pipeline",
            """Hi {name},

{trigger} stood out. Teams in that spot usually have demand — but the first conversation with new buyers is still manual and inconsistent.

I'm {sender} at {business}. We help B2B teams start more of those conversations with personalised email (not spray-and-pray).

Would {offer} help?

{sender}
{link}""",
        ),
        3: (
            "Where replies die at {company}",
            """Hi {name},

Quick follow-up. The pattern we see: good offers, weak first-touch copy, no Day-3 bump.

I can show you what a personalised sequence for buyers like your ICP looks like — {offer}.

{sender}""",
        ),
        7: (
            "Last note from me",
            """Hi {name},

I'll leave it here. If filling meetings for {company} is on your plate, {offer} is still open: {link}

{sender}
{business}""",
        ),
    },
    "accounting": {
        0: (
            "Books before the rush — {company}",
            """Hi {name},

With {trigger}, the messy part is usually the books catching up to the business.

I'm {sender} at {business}. We partner with SMEs that outgrow spreadsheet accounting.

Interested in {offer}?

{sender}
{link}""",
        ),
        3: (
            "Tax-season readiness",
            """Hi {name},

Following up. A short health check now beats a scramble later — happy to run {offer}.

{sender}""",
        ),
        7: (
            "Still relevant for {company}?",
            """Hi {name},

If you already have a sharp accounting partner, please ignore. Otherwise: {link}

{sender}
{business}""",
        ),
    },
    "consulting": {
        0: (
            "Ops note for {company}",
            """Hi {name},

{trigger} often exposes process bottlenecks that revenue hides. I'm {sender} at {business} — we help leadership teams find and fix those quietly.

Open to {offer}?

{sender}
{link}""",
        ),
        3: (
            "Three questions we ask",
            """Hi {name},

When we sit with a {title} after moments like yours, we start with three diagnostic questions. Happy to share them — or run {offer}.

{sender}""",
        ),
        7: (
            "Door's open",
            """Hi {name},

Last note from me. If useful: {link}

{sender}
{business}""",
        ),
    },
    "commercial_re": {
        0: (
            "Space timing for {company}",
            """Hi {name},

{trigger} — that's usually when space decisions get expensive if left late.

I'm {sender} at {business}. We match growing teams to the right commercial space without the cold-call carousel.

Worth {offer}?

{sender}
{link}""",
        ),
        3: (
            "Inventory brief",
            """Hi {name},

I can send a short brief of live options that fit teams like {company}. Or we do {offer} live.

{sender}""",
        ),
        7: (
            "Lease window",
            """Hi {name},

If the space question at {company} is settled, disregard. If not: {link}

{sender}
{business}""",
        ),
    },
    "recruiting": {
        0: (
            "Hiring at {company}",
            """Hi {name},

Saw {trigger}. Roles like that stall when sourcing is reactive.

I'm {sender} at {business}. We help hiring managers fill priority seats with less noise.

Would {offer} help?

{sender}
{link}""",
        ),
        3: (
            "Shortlist option",
            """Hi {name},

Happy to put {offer} in front of you this week — even if you're only comparing agencies.

{sender}""",
        ),
        7: (
            "Closing my loop",
            """Hi {name},

Last nudge. If the role is still open: {link}

{sender}
{business}""",
        ),
    },
    "legal": {
        0: (
            "Risk scan — {company}",
            """Hi {name},

{trigger} usually brings contract and compliance questions that sit in the inbox until they're urgent.

I'm {sender} at {business}. We help teams like yours get ahead of that.

Open to {offer}?

{sender}
{link}""",
        ),
        3: (
            "Written context first",
            """Hi {name},

I know cold calls are the worst for counsel. Happy to keep this in email — or schedule {offer}.

{sender}""",
        ),
        7: (
            "Final note",
            """Hi {name},

If timing's wrong at {company}, no worries. If useful: {link}

{sender}
{business}""",
        ),
    },
    "it_msp": {
        0: (
            "Resilience at {company}",
            """Hi {name},

{trigger} is a familiar signal — IT debt tends to surface right when growth accelerates.

I'm {sender} at {business}. We keep mid-market stacks stable so founders don't live in the server room.

Interested in {offer}?

{sender}
{link}""",
        ),
        3: (
            "Quiet checklist",
            """Hi {name},

I can send a one-page resilience checklist, or we can walk through {offer} together.

{sender}""",
        ),
        7: (
            "Leave it here",
            """Hi {name},

Last email from me. If uptime at {company} is on your mind: {link}

{sender}
{business}""",
        ),
    },
    "agency": {
        0: (
            "Brand moment at {company}",
            """Hi {name},

{trigger} — that's when the brand either looks ready or looks behind.

I'm {sender} at {business}. We help founders tighten story, site, and funnel without a six-month pitch theatre.

Worth {offer}?

{sender}
{link}""",
        ),
        3: (
            "Three concrete fixes",
            """Hi {name},

Happy to send three specific observations on {company}'s public presence — or do {offer} live.

{sender}""",
        ),
        7: (
            "Last creative nudge",
            """Hi {name},

I'll stop here. If a sharper brand helps {company} sell: {link}

{sender}
{business}""",
        ),
    },
}
