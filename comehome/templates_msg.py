"""Personal-feeling WhatsApp / SMS copy for 30 / 60 / 90 day touchpoints."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SequenceCopy:
    day: int
    subject: str
    body: str


# {client_name}, {business_name}, {staff_name}, {offer}, {booking_link}
SEQUENCES: dict[str, list[SequenceCopy]] = {
    "gym": [
        SequenceCopy(
            30,
            "We noticed the quiet",
            "Hi {client_name} — it’s {staff_name} from {business_name}. "
            "Haven’t seen you on the floor in a bit and wanted to check you’re okay. "
            "Your spot is still here whenever you’re ready. Want me to hold a session this week?",
        ),
        SequenceCopy(
            60,
            "Easy way back in",
            "{client_name}, quick one from {business_name}. "
            "Coming back after a break is the hard part — so we kept it simple. "
            "{offer} Reply YES and I’ll lock a time that works for you.",
        ),
        SequenceCopy(
            90,
            "Still saving your place",
            "Hi {client_name}, last note from me ({staff_name}). "
            "If fitness slipped down the list, no judgement — life in Harare gets full. "
            "If you want a soft restart, tap {booking_link} or reply and I’ll sort it. "
            "Either way, we’re glad you were part of {business_name}.",
        ),
    ],
    "chiro": [
        SequenceCopy(
            30,
            "How’s the body holding?",
            "Hi {client_name}, {staff_name} from {business_name} here. "
            "It’s been about a month since your last visit — how are you feeling? "
            "Happy to fit you in for a quick check if anything’s tightening up again.",
        ),
        SequenceCopy(
            60,
            "Care plan check-in",
            "{client_name}, following up from {business_name}. "
            "Maintenance visits are what keep the gains — {offer}. "
            "Reply with a day that suits you and we’ll reserve it.",
        ),
        SequenceCopy(
            90,
            "We’re still in your corner",
            "Hi {client_name} — {staff_name} again. "
            "If things settled and you don’t need us right now, that’s okay. "
            "If discomfort crept back, book here: {booking_link}. "
            "Your file is ready at {business_name}.",
        ),
    ],
    "spa": [
        SequenceCopy(
            30,
            "Your pause is noticed",
            "Hi {client_name}, it’s {staff_name} at {business_name}. "
            "We missed your usual visit and hoped you’re resting well. "
            "When you want an hour back for yourself, just reply — we’ll make space.",
        ),
        SequenceCopy(
            60,
            "A gentle reset",
            "{client_name}, a small invitation from {business_name}: {offer}. "
            "No pressure — only a soft way to return when life allows. "
            "Reply BOOK and I’ll send open times.",
        ),
        SequenceCopy(
            90,
            "The room is still yours",
            "Hi {client_name}. Last warm note from {staff_name}. "
            "If self-care went quiet, we understand. "
            "Whenever you’re ready: {booking_link}. {business_name} will be here.",
        ),
    ],
    "salon": [
        SequenceCopy(
            30,
            "Your chair misses you",
            "Hi {client_name} — {staff_name} from {business_name}. "
            "It’s been a while since your last appointment. "
            "Want me to pencil you in with your usual time?",
        ),
        SequenceCopy(
            60,
            "Keep the look fresh",
            "{client_name}, quick hello from {business_name}. "
            "{offer} Reply with a preferred day and I’ll confirm with {staff_name}.",
        ),
        SequenceCopy(
            90,
            "Still happy to have you",
            "Hi {client_name}, {staff_name} here. "
            "If you’ve found a new spot, all good. "
            "If you’d like to come back, book here: {booking_link}. "
            "We’d love to see you at {business_name} again.",
        ),
    ],
    "dental": [
        SequenceCopy(
            30,
            "Friendly recall",
            "Hi {client_name}, {business_name} here ({staff_name}). "
            "Just checking in — it’s been a month since we last saw you. "
            "Any sensitivity or due for a clean? Happy to help you book.",
        ),
        SequenceCopy(
            60,
            "Keep the smile easy",
            "{client_name}, a gentle reminder from {business_name}. "
            "{offer} Reply CALL and we’ll ring you to set a time.",
        ),
        SequenceCopy(
            90,
            "Your place on the diary",
            "Hi {client_name}. Final note from {staff_name} at {business_name}. "
            "Preventive visits are easier than urgent ones. "
            "Book when ready: {booking_link}.",
        ),
    ],
    "clinic": [
        SequenceCopy(
            30,
            "How are you getting on?",
            "Hi {client_name}, {staff_name} from {business_name}. "
            "Wanted to see how you’ve been since your last visit. "
            "If you need a follow-up, reply and we’ll arrange it.",
        ),
        SequenceCopy(
            60,
            "Continuity of care",
            "{client_name}, checking in from {business_name}. "
            "{offer} A short review visit can keep things on track — shall we book?",
        ),
        SequenceCopy(
            90,
            "We’re here when you need us",
            "Hi {client_name}. {staff_name} at {business_name}. "
            "No pressure — only an open door. "
            "Book here anytime: {booking_link}.",
        ),
    ],
    "optical": [
        SequenceCopy(
            30,
            "Eyes need love too",
            "Hi {client_name}, {staff_name} from {business_name}. "
            "It’s been a month since your last visit — any strain or blur lately? "
            "We can fit a quick check if useful.",
        ),
        SequenceCopy(
            60,
            "Time for a refresh?",
            "{client_name}, hello from {business_name}. "
            "{offer} Reply YES and we’ll send available slots.",
        ),
        SequenceCopy(
            90,
            "Still looking out for you",
            "Hi {client_name} — last note from {staff_name}. "
            "When you’re ready for an exam or new frames: {booking_link}. "
            "{business_name} keeps your prescription on file.",
        ),
    ],
    "sports": [
        SequenceCopy(
            30,
            "Training gap check",
            "Hi {client_name}, Coach {staff_name} from {business_name}. "
            "Missed you at sessions lately — everything alright? "
            "Happy to help plan a gentle return to training.",
        ),
        SequenceCopy(
            60,
            "Come back to the pitch",
            "{client_name}, {business_name} here. "
            "{offer} Reply and we’ll get {client_name} back on the plan.",
        ),
        SequenceCopy(
            90,
            "The squad still has room",
            "Hi — final note from Coach {staff_name} at {business_name}. "
            "If the break became permanent, we understand. "
            "If you want back in: {booking_link}.",
        ),
    ],
    "tutor": [
        SequenceCopy(
            30,
            "Lessons pause check",
            "Hi {client_name}, {staff_name} from {business_name}. "
            "We noticed lessons paused and wanted to make sure everything is okay. "
            "Ready to restart when you are.",
        ),
        SequenceCopy(
            60,
            "Keep the momentum",
            "{client_name}, a note from {business_name}. "
            "{offer} Reply with preferred days and we’ll rebuild the timetable.",
        ),
        SequenceCopy(
            90,
            "Door stays open",
            "Hi {client_name}. {staff_name} at {business_name}. "
            "If tutoring isn’t needed right now, no problem. "
            "When exams approach: {booking_link}.",
        ),
    ],
    "beauty": [
        SequenceCopy(
            30,
            "Missed your appointment glow",
            "Hi {client_name}, {staff_name} at {business_name}. "
            "It’s been a minute — want me to reserve your usual slot this week?",
        ),
        SequenceCopy(
            60,
            "A soft comeback",
            "{client_name}, {business_name} here. "
            "{offer} Reply BOOK and I’ll send times.",
        ),
        SequenceCopy(
            90,
            "Always welcome back",
            "Hi {client_name}. Last message from {staff_name}. "
            "Your chair is open whenever you are: {booking_link}. "
            "— {business_name}",
        ),
    ],
    "vet": [
        SequenceCopy(
            30,
            "How’s your furry one?",
            "Hi {client_name}, {staff_name} from {business_name}. "
            "Just checking on your pet since the last visit. "
            "Any concerns, or due for a follow-up? Reply anytime.",
        ),
        SequenceCopy(
            60,
            "Health stays on schedule",
            "{client_name}, friendly nudge from {business_name}. "
            "{offer} We can book a quick wellness slot — reply YES.",
        ),
        SequenceCopy(
            90,
            "We’re still their clinic",
            "Hi {client_name}. {staff_name} at {business_name}. "
            "When vaccines or check-ups are due: {booking_link}. "
            "We’re glad to care for them again whenever you’re ready.",
        ),
    ],
    "auto": [
        SequenceCopy(
            30,
            "Car missing its shine?",
            "Hi {client_name}, {staff_name} from {business_name}. "
            "Haven’t seen your car in a while — want a wash slot this week?",
        ),
        SequenceCopy(
            60,
            "Easy restart",
            "{client_name}, {business_name} here. "
            "{offer} Reply WASH and we’ll confirm a time.",
        ),
        SequenceCopy(
            90,
            "Membership still open",
            "Hi {client_name}. Final note from {staff_name}. "
            "If you want back on the plan: {booking_link}. "
            "— {business_name}",
        ),
    ],
}


DEFAULT_OFFERS = {
    "gym": "Your first week back is on a soft restart rate",
    "chiro": "Complimentary posture screen with your next visit",
    "spa": "Complimentary upgrade on your next 60-minute treatment",
    "salon": "Complimentary finish / style refresh with your next booking",
    "dental": "Priority morning slot held for returning patients this week",
    "clinic": "Short review consultation at returning-patient rate",
    "optical": "Frame refresh consult with exam priority this fortnight",
    "sports": "Two complimentary return sessions for the athlete",
    "tutor": "One diagnostic lesson to map the catch-up plan",
    "beauty": "Complimentary add-on on your next visit",
    "vet": "Wellness check priority booking this month",
    "auto": "Member wash rate reinstated on your next visit",
}


def render_sequence(
    vertical: str,
    day: int,
    *,
    client_name: str,
    business_name: str,
    staff_name: str = "the team",
    offer: str | None = None,
    booking_link: str = "https://comehome.example/book",
) -> SequenceCopy:
    steps = SEQUENCES.get(vertical, SEQUENCES["gym"])
    step = next((s for s in steps if s.day == day), steps[-1])
    body = step.body.format(
        client_name=client_name.split()[0],
        business_name=business_name,
        staff_name=staff_name,
        offer=offer or DEFAULT_OFFERS.get(vertical, "A simple welcome-back offer"),
        booking_link=booking_link,
    )
    return SequenceCopy(day=step.day, subject=step.subject, body=body)


def all_days() -> tuple[int, ...]:
    return (30, 60, 90)
