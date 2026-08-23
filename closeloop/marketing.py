"""Catalogue + social advert copy for contractor acquisition."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdvertPiece:
    channel: str
    title: str
    headline: str
    body: str
    cta: str
    hashtags: str = ""


STEP_BY_STEP_REGISTER = (
    {
        "step": 1,
        "title": "Click the signup link",
        "detail": "Open the CloseLoop link from an ad, catalogue QR, or referral: /register",
    },
    {
        "step": 2,
        "title": "Register your company",
        "detail": "Enter company name, your name, trade, phone, work email, and a password.",
    },
    {
        "step": 3,
        "title": "Pick your plan",
        "detail": "Starter $500 · Growth $997 · Scale $1,500 — change later as you grow.",
    },
    {
        "step": 4,
        "title": "Add your first client",
        "detail": "After each estimate visit, log homeowner name, WhatsApp number, email, address, and quote amount.",
    },
    {
        "step": 5,
        "title": "Follow-ups run automatically",
        "detail": "Day 2, Day 5, and Day 10 WhatsApp + email messages schedule themselves. Call scripts appear on your dashboard.",
    },
    {
        "step": 6,
        "title": "Mark won or lost",
        "detail": "When they book — or choose someone else — update status. Remaining messages stop.",
    },
)


ADVANTAGES = (
    {
        "title": "Stop losing jobs to silence",
        "detail": "Homeowners go with whoever follows up. CloseLoop makes sure that’s you.",
    },
    {
        "title": "WhatsApp + email on autopilot",
        "detail": "No sticky notes. No forgotten callbacks. Day 2 / 5 / 10 run while you work.",
    },
    {
        "title": "Built for your trade",
        "detail": "Roofers, painters, landscapers, construction, HVAC, and more — with scripts that sound human.",
    },
    {
        "title": "Pays for itself fast",
        "detail": "One saved mid-ticket job covers months of Starter, Growth, or Scale.",
    },
    {
        "title": "Ready in minutes",
        "detail": "Click link → register company → add clients. No IT project.",
    },
    {
        "title": "Clear pipeline",
        "detail": "See open value, due follow-ups, and call scripts every morning.",
    },
)


SOCIAL_POSTERS: tuple[AdvertPiece, ...] = (
    AdvertPiece(
        channel="Instagram / Facebook square",
        title="Silence loses jobs",
        headline="You quoted it. Don’t ghost it.",
        body=(
            "Contractors lose work after the estimate because nobody follows up.\n"
            "CloseLoop sends Day 2, Day 5 & Day 10 WhatsApp + email for you."
        ),
        cta="Register free → closeloop.link/register",
        hashtags="#ContractorLife #Roofing #Painting #Landscaping #CloseMoreJobs",
    ),
    AdvertPiece(
        channel="Facebook / LinkedIn feed",
        title="45 minutes on-site",
        headline="45 minutes quoting. Zero follow-up. Job gone.",
        body=(
            "After the site visit, CloseLoop chases the homeowner automatically:\n"
            "• Day 2 soft check-in\n• Day 5 value + urgency\n• Day 10 decision close\n"
            "WhatsApp + email. Built for trades."
        ),
        cta="Start your company account today → /register",
        hashtags="#HomeServices #ConstructionBusiness #SalesFollowUp",
    ),
    AdvertPiece(
        channel="WhatsApp status / Story",
        title="Story sticker",
        headline="Stop losing jobs to whoever calls back.",
        body="Tap to register your crew. Auto WhatsApp + email follow-ups for every estimate.",
        cta="Link in bio → /register",
        hashtags="",
    ),
    AdvertPiece(
        channel="TikTok / Reels caption",
        title="Hook + CTA",
        headline="POV: you sent the estimate and never followed up…",
        body=(
            "Homeowner picked the contractor who WhatsApp’d them on Day 2.\n"
            "CloseLoop does Day 2 / 5 / 10 for roofers, painters & landscapers."
        ),
        cta="Comment CLOSE and we’ll DM the signup link",
        hashtags="#ContractorsOfTikTok #RoofTok #PaintTok",
    ),
    AdvertPiece(
        channel="Google / Meta ad (short)",
        title="Search / PPC",
        headline="Automatic estimate follow-ups for contractors",
        body="WhatsApp + email Day 2, 5, 10. Close more of the jobs you already quoted. From $500/mo.",
        cta="Register your company → /register",
        hashtags="",
    ),
)


CATALOGUE_PAGES: tuple[AdvertPiece, ...] = (
    AdvertPiece(
        channel="Catalogue cover",
        title="Cover line",
        headline="CloseLoop — the callback system for contractors",
        body="Never lose a quoted job to silence again.",
        cta="Scan to register your company",
        hashtags="",
    ),
    AdvertPiece(
        channel="Catalogue — problem page",
        title="The leak in your sales",
        headline="Quotes don’t close themselves",
        body=(
            "You drive out. You measure. You send the number.\n"
            "Then the phone goes quiet — and another crew wins by simply calling back."
        ),
        cta="See how CloseLoop fixes it →",
        hashtags="",
    ),
    AdvertPiece(
        channel="Catalogue — solution page",
        title="How it works",
        headline="Register. Add clients. We chase.",
        body=(
            "1) Click the link and register your company\n"
            "2) After each estimate, enter the client once\n"
            "3) WhatsApp + email fire on Day 2, 5, and 10\n"
            "4) Mark won/lost when the job decides"
        ),
        cta="Plans from $500 / $997 / $1,500 per month",
        hashtags="",
    ),
    AdvertPiece(
        channel="Catalogue — trades page",
        title="Who it’s for",
        headline="Playbooks for estimate-heavy trades",
        body=(
            "Roofing · Painting · Landscaping · Construction\n"
            "HVAC · Plumbing · Electrical · Flooring\n"
            "Concrete · Windows & Doors · Fencing · Remodeling · Pest"
        ),
        cta="Pick your trade at signup",
        hashtags="",
    ),
    AdvertPiece(
        channel="Catalogue — offer page",
        title="Pricing strip",
        headline="One saved job pays for the software",
        body=(
            "Starter $500/mo — solo operators\n"
            "Growth $997/mo — growing crews\n"
            "Scale $1,500/mo — multi-crew companies"
        ),
        cta="Register now — start adding clients today",
        hashtags="",
    ),
)


FLYER_BLURB = (
    "CLOSELOOP\n"
    "Automatic WhatsApp + email follow-ups for contractors\n"
    "Day 2 · Day 5 · Day 10\n\n"
    "1. Scan / open the link\n"
    "2. Register your company\n"
    "3. Add clients after every quote\n"
    "4. We chase so you can close\n\n"
    "From $500/mo  |  Roofers · Painters · Landscapers · Construction"
)