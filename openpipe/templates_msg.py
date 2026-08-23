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


@dataclass(frozen=True)
class WhatsAppCopy:
    day: int
    body: str


def first_name(full_name: str) -> str:
    return (full_name or "there").strip().split()[0]


def all_days() -> tuple[int, ...]:
    return SEQUENCE_DAYS


def sample_sequences(verticals: tuple[str, ...] | None = None) -> list[dict]:
    """Marketing-site samples for the three core ICPs."""
    from .starters import CORE_VERTICALS, SAMPLE_PROSPECTS

    keys = verticals or CORE_VERTICALS
    out: list[dict] = []
    for vertical in keys:
        ctx = SAMPLE_PROSPECTS.get(vertical, SAMPLE_PROSPECTS["insurance"])
        days = []
        for day in SEQUENCE_DAYS:
            email = render_sequence(vertical, day, **ctx)
            wa = render_whatsapp(vertical, day, **ctx)
            days.append(
                {
                    "day": day,
                    "subject": email.subject,
                    "body": email.body,
                    "whatsapp": wa.body,
                }
            )
        out.append(
            {
                "vertical": vertical,
                "label": {
                    "insurance": "Insurance brokers",
                    "advisor": "Financial advisors",
                    "b2b": "B2B services",
                }.get(vertical, vertical),
                "prospect": ctx["prospect_name"],
                "company": ctx["company"],
                "trigger": ctx["trigger"],
                "days": days,
            }
        )
    return out


def _ctx(
    *,
    prospect_name: str,
    company: str,
    title: str,
    trigger: str,
    sender_name: str,
    business_name: str,
    offer: str | None,
    booking_link: str,
    vertical: str,
) -> dict[str, str]:
    return {
        "name": first_name(prospect_name),
        "full_name": prospect_name,
        "company": company,
        "title": title,
        "trigger": trigger,
        "sender": sender_name,
        "business": business_name,
        "offer": offer or DEFAULT_OFFERS.get(vertical, DEFAULT_OFFERS["b2b"]),
        "link": booking_link,
    }


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
    ctx = _ctx(
        prospect_name=prospect_name,
        company=company,
        title=title,
        trigger=trigger,
        sender_name=sender_name,
        business_name=business_name,
        offer=offer,
        booking_link=booking_link,
        vertical=vertical,
    )
    templates = _TEMPLATES.get(vertical, _TEMPLATES["b2b"])
    day_key = day if day in templates else 0
    subject_tpl, body_tpl = templates[day_key]
    return EmailCopy(
        day=day_key,
        subject=subject_tpl.format(**ctx),
        body=body_tpl.format(**ctx).strip(),
    )


def render_whatsapp(
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
) -> WhatsAppCopy:
    ctx = _ctx(
        prospect_name=prospect_name,
        company=company,
        title=title,
        trigger=trigger,
        sender_name=sender_name,
        business_name=business_name,
        offer=offer,
        booking_link=booking_link,
        vertical=vertical,
    )
    templates = _WA_TEMPLATES.get(vertical, _WA_TEMPLATES["b2b"])
    day_key = day if day in templates else 0
    return WhatsAppCopy(day=day_key, body=templates[day_key].format(**ctx).strip())


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


# Short WhatsApp variants — same Day 0 / 3 / 7 cadence, fewer lines.
_WA_TEMPLATES: dict[str, dict[int, str]] = {
    "insurance": {
        0: "Hi {name} — saw {trigger}. Congrats. Growth like that often creates cover gaps. {sender} at {business} here. Open to {offer}? {link}",
        3: "Hi {name}, quick bump on cover for {company}. Happy to send a 1-page checklist or do {offer}. — {sender}",
        7: "{name}, last note — if cover at {company} isn't sorted, {offer} is open: {link} — {sender}",
    },
    "advisor": {
        0: "Hi {name} — {trigger} usually shifts cash-flow/tax/personal planning. {sender} ({business}). Open to {offer}? {link}",
        3: "{name}, I can walk you through a short snapshot we use after moments like yours. {offer}? — {sender}",
        7: "Closing the loop, {name}. If timing's right at {company}: {link} — {sender}",
    },
    "b2b": {
        0: "Hi {name} — {trigger} stood out. We help B2B teams start buyer conversations with personalised outreach. {offer}? — {sender}, {business} {link}",
        3: "{name}, pattern we see: good offers, weak first-touch. Happy to show a sample sequence — {offer}. — {sender}",
        7: "Last note from me, {name}. If filling meetings for {company} is on your plate: {link} — {sender}",
    },
    "accounting": {
        0: "Hi {name} — with {trigger}, books often lag the business. {sender} at {business}. Interested in {offer}? {link}",
        3: "{name}, short health check now beats a scramble later — {offer}. — {sender}",
        7: "Still relevant for {company}? {link} — {sender}",
    },
    "consulting": {
        0: "Hi {name} — {trigger}. {sender} ({business}). Open to {offer}? {link}",
        3: "{name}, happy to share how similar firms unblocked this — or do {offer}. — {sender}",
        7: "Last nudge for {company}: {link} — {sender}",
    },
    "commercial_re": {
        0: "Hi {name} — {trigger}. Space needs shift fast. {sender} at {business}. {offer}? {link}",
        3: "{name}, can send a short space brief matched to inventory — {offer}. — {sender}",
        7: "If {company} still needs space: {link} — {sender}",
    },
    "recruiting": {
        0: "Hi {name} — saw {trigger}. {sender} ({business}). Can share {offer}. {link}",
        3: "{name}, still hiring? Happy to send three fits or do {offer}. — {sender}",
        7: "Last nudge if the role's open: {link} — {sender}",
    },
    "legal": {
        0: "Hi {name} — {trigger} usually brings contract/compliance questions. {sender} at {business}. {offer}? {link}",
        3: "{name}, happy to keep this in writing — or schedule {offer}. — {sender}",
        7: "If timing's wrong, ignore. Else: {link} — {sender}",
    },
    "it_msp": {
        0: "Hi {name} — {trigger}. IT debt shows up when growth accelerates. {sender} ({business}). {offer}? {link}",
        3: "{name}, can send a resilience checklist or do {offer}. — {sender}",
        7: "Last note on uptime at {company}: {link} — {sender}",
    },
    "agency": {
        0: "Hi {name} — {trigger}. Brand either looks ready or behind. {sender} at {business}. Worth {offer}? {link}",
        3: "{name}, happy to send 3 concrete fixes on {company}'s public presence — or {offer}. — {sender}",
        7: "Last creative nudge: {link} — {sender}",
    },
}
