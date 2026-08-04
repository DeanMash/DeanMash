"""Business verticals suited to 30/60/90 win-back — focused on Zimbabwe & similar markets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vertical:
    key: str
    label: str
    why: str
    lapse_signal: str
    channel_note: str


VERTICALS: dict[str, Vertical] = {
    "gym": Vertical(
        key="gym",
        label="Gyms & fitness centres",
        why="Memberships quietly expire when nobody notices the silence.",
        lapse_signal="Last check-in / last class attended",
        channel_note="WhatsApp feels like a coach checking in — not a billing reminder.",
    ),
    "chiro": Vertical(
        key="chiro",
        label="Chiropractors & physiotherapists",
        why="Care plans stall after the pain eases; follow-ups protect outcomes and revenue.",
        lapse_signal="Last adjustment / last physio session",
        channel_note="A personal note from the practice beats a generic SMS.",
    ),
    "spa": Vertical(
        key="spa",
        label="Spas, massage & wellness",
        why="Self-care is the first budget cut — a warm nudge restarts the habit.",
        lapse_signal="Last treatment booking",
        channel_note="Short, sensory language works better than discount blasts.",
    ),
    "salon": Vertical(
        key="salon",
        label="Hair salons & barbershops",
        why="Clients drift to whoever is closer — loyalty is won between appointments.",
        lapse_signal="Last cut / colour / braid appointment",
        channel_note="Mention their usual stylist by name when you can.",
    ),
    "dental": Vertical(
        key="dental",
        label="Dental clinics",
        why="Six-month recalls fail when life gets busy; early touchpoints keep diaries full.",
        lapse_signal="Last cleaning / last visit",
        channel_note="Friendly reminder + easy reply-to-book converts well.",
    ),
    "clinic": Vertical(
        key="clinic",
        label="Private medical & aesthetic clinics",
        why="Repeat visits drop without structured outreach after the first course of care.",
        lapse_signal="Last consultation",
        channel_note="Keep tone clinical-warm; never alarmist.",
    ),
    "optical": Vertical(
        key="optical",
        label="Optometrists & eye clinics",
        why="Lens checks and frame refreshes are easy to postpone indefinitely.",
        lapse_signal="Last eye exam",
        channel_note="Anniversary-style messaging performs strongly.",
    ),
    "sports": Vertical(
        key="sports",
        label="Sports academies & coaching",
        why="Young athletes pause for school or travel and never restart without a push.",
        lapse_signal="Last training session",
        channel_note="Message parents on WhatsApp; keep it encouraging.",
    ),
    "tutor": Vertical(
        key="tutor",
        label="Tutoring & education centres",
        why="Term breaks become permanent drop-offs when nobody follows up.",
        lapse_signal="Last lesson / last term attended",
        channel_note="Reference the learner’s subject and next exam window.",
    ),
    "beauty": Vertical(
        key="beauty",
        label="Nail bars & beauty studios",
        why="High frequency clients are also the fastest to vanish without a schedule.",
        lapse_signal="Last appointment",
        channel_note="Offer a simple slot, not a catalogue of services.",
    ),
    "vet": Vertical(
        key="vet",
        label="Veterinary clinics",
        why="Annual vaccines and check-ups slip when owners are not prompted.",
        lapse_signal="Last visit / last vaccine due",
        channel_note="Use the pet’s name — it makes the message feel personal instantly.",
    ),
    "auto": Vertical(
        key="auto",
        label="Car wash & detailing clubs",
        why="Monthly wash plans die the week a client gets busy.",
        lapse_signal="Last wash / last membership visit",
        channel_note="A one-tap ‘book this week’ link recovers routines fast.",
    ),
}


def list_verticals() -> list[Vertical]:
    return list(VERTICALS.values())


def get_vertical(key: str) -> Vertical:
    return VERTICALS.get(key, VERTICALS["gym"])
