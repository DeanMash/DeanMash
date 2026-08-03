"""Trade verticals and Day 2 / Day 5 / Day 10 follow-up copy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FollowUpCopy:
    day: int
    channel: str  # sms | email | call_script
    subject: str | None
    body: str
    intent: str


@dataclass(frozen=True)
class TradeProfile:
    key: str
    label: str
    emoji: str
    avg_ticket: str
    pain_point: str
    sequences: tuple[FollowUpCopy, ...]


def _seq(
    day2_sms: str,
    day2_email_subject: str,
    day2_email: str,
    day5_sms: str,
    day5_email_subject: str,
    day5_email: str,
    day5_call: str,
    day10_sms: str,
    day10_email_subject: str,
    day10_email: str,
    day10_call: str,
) -> tuple[FollowUpCopy, ...]:
    return (
        FollowUpCopy(2, "sms", None, day2_sms, "soft_check_in"),
        FollowUpCopy(2, "email", day2_email_subject, day2_email, "soft_check_in"),
        FollowUpCopy(5, "sms", None, day5_sms, "value_nudge"),
        FollowUpCopy(5, "email", day5_email_subject, day5_email, "value_nudge"),
        FollowUpCopy(5, "call_script", "Day 5 call", day5_call, "phone_close"),
        FollowUpCopy(10, "sms", None, day10_sms, "decision_close"),
        FollowUpCopy(10, "email", day10_email_subject, day10_email, "decision_close"),
        FollowUpCopy(10, "call_script", "Day 10 call", day10_call, "final_close"),
    )


TRADES: dict[str, TradeProfile] = {
    "roofing": TradeProfile(
        key="roofing",
        label="Roofing",
        emoji="🏠",
        avg_ticket="$8k–$25k",
        pain_point="Homeowners get 3 quotes and pick whoever follows up first.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} here — just checking you received the "
                "roof estimate for {address} (${estimate_amount}). Happy to answer any "
                "questions. — {owner_name}"
            ),
            day2_email_subject="Your roof estimate for {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Thanks again for having us out. Your estimate for the roof work at "
                "{address} is ${estimate_amount}.\n\n"
                "Most of our customers have questions about materials, timeline, or "
                "insurance. Reply to this email or call {company_phone} and I’ll walk "
                "you through it.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "Quick update from {company}: we’ve got a crew window opening soon near "
                "{address}. Want me to hold a start date while you decide? — {owner_name}"
            ),
            day5_email_subject="Crew availability near {address}",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "Wanted to share that we’re scheduling work in your area over the next "
                "few weeks. If you’d like the ${estimate_amount} roof project locked in, "
                "I can hold a start date.\n\n"
                "Also happy to review a competitor quote side-by-side — no pressure.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, this is {owner_name} with {company}. Calling about "
                "the roof estimate we sent for {address}. Did you get a chance to look it "
                "over? … What’s the main thing holding the decision — price, timing, or "
                "comparing other bids? … We can hold a crew date if that helps."
            ),
            day10_sms=(
                "Last check-in from {company} on the {address} roof quote "
                "(${estimate_amount}). Should I close the file or set a start date? "
                "Text YES or CALL. — {owner_name}"
            ),
            day10_email_subject="Closing out your roof quote — {address}",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "I don’t want to keep pinging you — just need to know if we should keep "
                "the ${estimate_amount} estimate active for {address}.\n\n"
                "Reply YES to book, HOLD if you need more time, or NO and I’ll close "
                "the file with no hard feelings.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final follow-up on the "
                "roof quote for {address}. Are you moving forward with us, still deciding, "
                "or going another direction? I can book you this week or close the file."
            ),
        ),
    ),
    "painting": TradeProfile(
        key="painting",
        label="Painting",
        emoji="🎨",
        avg_ticket="$2k–$12k",
        pain_point="Cheap bids win on silence — a timed follow-up protects margin.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — confirming you got the paint estimate "
                "for {address} (${estimate_amount}). Questions on colors or prep? "
                "— {owner_name}"
            ),
            day2_email_subject="Paint estimate ready — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your painting estimate for {address} is ${estimate_amount}. It covers "
                "prep, materials, and the finish we discussed on-site.\n\n"
                "If you want color samples or a phased plan (exterior first, interiors "
                "later), I can adjust the quote same-day.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: weather/crew openings look good for {address} next week. "
                "Want the ${estimate_amount} paint job on the schedule? — {owner_name}"
            ),
            day5_email_subject="Scheduling your paint project",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "We’re filling the calendar for the next 10–14 days. Your project at "
                "{address} (${estimate_amount}) can slot in if we confirm soon.\n\n"
                "Tip: locking a date early avoids rush premiums during busy season.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Checking on the paint "
                "estimate for {address}. Any color or scope changes since we met? We can "
                "hold a start date this week if you’re ready."
            ),
            day10_sms=(
                "Final note from {company} on {address} (${estimate_amount}). Book, hold, "
                "or close the quote? — {owner_name}"
            ),
            day10_email_subject="Keep your paint quote open?",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Quick decision check on the ${estimate_amount} painting estimate for "
                "{address}. Reply YES / HOLD / NO and I’ll handle the rest.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, last call from {owner_name} at {company} about the "
                "paint job at {address}. Ready to schedule, need a revision, or should I "
                "close the estimate?"
            ),
        ),
    ),
    "landscaping": TradeProfile(
        key="landscaping",
        label="Landscaping",
        emoji="🌿",
        avg_ticket="$1.5k–$20k",
        pain_point="Seasonal windows close fast — follow-ups book the backlog.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} here. Hope you saw the landscape proposal "
                "for {address} (${estimate_amount}). Want a quick walkthrough? — {owner_name}"
            ),
            day2_email_subject="Landscape proposal — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Attached/sent was your landscaping proposal for {address} at "
                "${estimate_amount}. Happy to split it into phases if budget timing matters.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: plant/material lead times are moving. Still want us for "
                "{address}? I can reserve your install week. — {owner_name}"
            ),
            day5_email_subject="Reserve your install window",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "Materials and crew slots for projects like yours are booking up. If you’d "
                "like the ${estimate_amount} plan for {address}, I can reserve an install "
                "window now.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Calling about the "
                "landscape proposal for {address}. Any changes to scope or budget? We can "
                "phase it or lock an install week."
            ),
            day10_sms=(
                "Last follow-up from {company} on {address} (${estimate_amount}). Keep the "
                "proposal open or close it out? — {owner_name}"
            ),
            day10_email_subject="Closing your landscape proposal?",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Need a yes/no on the ${estimate_amount} landscaping proposal for "
                "{address} so we can free the calendar for other installs.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final check on the "
                "landscape work at {address}. Shall we schedule, revise, or close the file?"
            ),
        ),
    ),
    "general_construction": TradeProfile(
        key="general_construction",
        label="General Construction",
        emoji="🔨",
        avg_ticket="$10k–$100k+",
        pain_point="Long sales cycles die without a structured chase.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — confirming receipt of the construction "
                "estimate for {address} (${estimate_amount}). Questions welcome. — {owner_name}"
            ),
            day2_email_subject="Construction estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Thank you for the site visit. Your construction estimate for {address} "
                "is ${estimate_amount}. I’m available to review line items, allowances, "
                "and timeline in a short call.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: following up on {address}. Want a 10-min walkthrough of the "
                "${estimate_amount} estimate this week? — {owner_name}"
            ),
            day5_email_subject="Walk through the numbers?",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "Happy to jump on a quick call to compare options or adjust scope on the "
                "${estimate_amount} estimate for {address}. Many clients tighten the bid "
                "once we prioritize must-haves vs nice-to-haves.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Checking in on the "
                "estimate for {address}. What’s the biggest open question — budget, "
                "timeline, or scope? Let’s solve that today."
            ),
            day10_sms=(
                "{company}: deciding on {address} (${estimate_amount})? Reply YES to "
                "proceed, REVISE for changes, or NO to close. — {owner_name}"
            ),
            day10_email_subject="Decision needed — {address} estimate",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Please let us know how you’d like to proceed with the ${estimate_amount} "
                "estimate for {address}. If priorities changed, we can revise rather than "
                "lose the plan entirely.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final follow-up on "
                "{address}. Are we building, revising the estimate, or closing it out?"
            ),
        ),
    ),
    "hvac": TradeProfile(
        key="hvac",
        label="HVAC",
        emoji="❄️",
        avg_ticket="$4k–$15k",
        pain_point="Comfort is urgent — first callback usually wins the replace.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — did you get the HVAC estimate for "
                "{address} (${estimate_amount})? I can explain options in plain English. "
                "— {owner_name}"
            ),
            day2_email_subject="HVAC options for {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your HVAC estimate for {address} is ${estimate_amount}. I outlined "
                "repair vs replace so you can choose with confidence.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: equipment lead times apply on some units. Want me to hold "
                "pricing for {address}? — {owner_name}"
            ),
            day5_email_subject="Hold your HVAC pricing?",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "If you’re leaning toward the ${estimate_amount} option for {address}, "
                "I can hold equipment and an install slot. Financing options available "
                "if helpful.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Calling about the HVAC "
                "estimate at {address}. Repair or replace leaning either way? I can hold "
                "an install day."
            ),
            day10_sms=(
                "Last check from {company} on {address} HVAC (${estimate_amount}). Book "
                "or close the quote? — {owner_name}"
            ),
            day10_email_subject="HVAC quote follow-up — {address}",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Need your direction on the ${estimate_amount} HVAC estimate for "
                "{address}. Reply and we’ll schedule or close the file.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final follow-up on your "
                "HVAC quote for {address}. Ready to schedule install/repair?"
            ),
        ),
    ),
    "plumbing": TradeProfile(
        key="plumbing",
        label="Plumbing",
        emoji="🚿",
        avg_ticket="$500–$8k",
        pain_point="Emergency trust fades fast if nobody follows the quote.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} checking in on the plumbing estimate for "
                "{address} (${estimate_amount}). Still need this handled? — {owner_name}"
            ),
            day2_email_subject="Plumbing estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your plumbing estimate for {address} is ${estimate_amount}. We can often "
                "schedule within a few days once approved.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: opening on the schedule near {address}. Approve the "
                "${estimate_amount} work and I’ll book you. — {owner_name}"
            ),
            day5_email_subject="We can get you on the schedule",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "We have availability coming up. If you’d like to move forward on "
                "{address} for ${estimate_amount}, reply and I’ll confirm a tech visit.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Following up on the "
                "plumbing quote for {address}. Is the issue still occurring? We can book "
                "as soon as you approve."
            ),
            day10_sms=(
                "Final note — {company} plumbing quote for {address} (${estimate_amount}). "
                "Proceed or close? — {owner_name}"
            ),
            day10_email_subject="Close your plumbing quote?",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Please advise on the ${estimate_amount} plumbing estimate for {address}. "
                "Happy to proceed, revise, or close it out.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Last follow-up on the "
                "plumbing work at {address}. Want us to schedule it?"
            ),
        ),
    ),
    "electrical": TradeProfile(
        key="electrical",
        label="Electrical",
        emoji="⚡",
        avg_ticket="$400–$10k",
        pain_point="Safety jobs stall without a confident, timely chase.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — confirming your electrical estimate for "
                "{address} (${estimate_amount}). Questions on scope/permits? — {owner_name}"
            ),
            day2_email_subject="Electrical estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your electrical estimate for {address} is ${estimate_amount}. Includes "
                "the work we scoped on-site; permits called out if needed.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: we can prioritize {address} this week if you approve "
                "${estimate_amount}. Want the slot? — {owner_name}"
            ),
            day5_email_subject="Priority scheduling available",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "If the ${estimate_amount} electrical work at {address} is still needed, "
                "we can prioritize scheduling. Reply and I’ll confirm.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Checking on the "
                "electrical estimate for {address}. Any concerns on price or timing?"
            ),
            day10_sms=(
                "Last follow-up from {company} on {address} (${estimate_amount}). Book or "
                "close the electrical quote? — {owner_name}"
            ),
            day10_email_subject="Electrical quote status — {address}",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Need a decision on the ${estimate_amount} electrical estimate for "
                "{address}. Reply YES / HOLD / NO.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final check on electrical "
                "work at {address}. Ready to schedule?"
            ),
        ),
    ),
    "flooring": TradeProfile(
        key="flooring",
        label="Flooring",
        emoji="🪵",
        avg_ticket="$2k–$15k",
        pain_point="Showroom shoppers ghost — sequenced follow-ups reopen the sale.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — your flooring estimate for {address} "
                "(${estimate_amount}) is ready. Want help picking the final material? "
                "— {owner_name}"
            ),
            day2_email_subject="Flooring estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your flooring estimate for {address} is ${estimate_amount}. If you’d like "
                "to see alternate materials at different price points, I can revise fast.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: material stock looks good for {address}. Lock the "
                "${estimate_amount} install? — {owner_name}"
            ),
            day5_email_subject="Material availability update",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "The materials for your ${estimate_amount} flooring project at {address} "
                "are available. Approving soon keeps your install date from slipping.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Following up on flooring "
                "for {address}. Still happy with the selection, or want options?"
            ),
            day10_sms=(
                "Final note from {company} on {address} flooring (${estimate_amount}). "
                "Proceed or close? — {owner_name}"
            ),
            day10_email_subject="Flooring quote — keep open?",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Please let me know on the ${estimate_amount} flooring estimate for "
                "{address}. Happy to revise species/style if that unblocks you.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Last follow-up on flooring "
                "at {address}. Book the install or close the quote?"
            ),
        ),
    ),
    "concrete": TradeProfile(
        key="concrete",
        label="Concrete & Masonry",
        emoji="🧱",
        avg_ticket="$3k–$30k",
        pain_point="Weather + schedule pressure — follow-ups fill the pour calendar.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — confirming the concrete estimate for "
                "{address} (${estimate_amount}). Questions on finish/timeline? — {owner_name}"
            ),
            day2_email_subject="Concrete estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your concrete/masonry estimate for {address} is ${estimate_amount}. "
                "We can discuss finish options and pour windows anytime.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: good pour weather windows coming up. Reserve {address} for "
                "${estimate_amount}? — {owner_name}"
            ),
            day5_email_subject="Pour window availability",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "We’re lining up pours and forming crews. If you want the "
                "${estimate_amount} work at {address}, I can reserve a weather window.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Checking on the concrete "
                "estimate for {address}. Ready to lock a pour date?"
            ),
            day10_sms=(
                "Last check-in — {company} on {address} (${estimate_amount}). Book the "
                "pour or close the quote? — {owner_name}"
            ),
            day10_email_subject="Concrete quote decision — {address}",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Need your go-ahead or a close-out on the ${estimate_amount} estimate for "
                "{address}.\n\n— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final follow-up on "
                "concrete work at {address}. Shall we schedule?"
            ),
        ),
    ),
    "windows_doors": TradeProfile(
        key="windows_doors",
        label="Windows & Doors",
        emoji="🪟",
        avg_ticket="$3k–$20k",
        pain_point="Long manufacturer lead times punish slow follow-up.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — your windows/doors estimate for "
                "{address} (${estimate_amount}) is in. Want help comparing options? "
                "— {owner_name}"
            ),
            day2_email_subject="Windows & doors estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your windows & doors estimate for {address} is ${estimate_amount}. "
                "I can review energy ratings and lead times if useful.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: ordering soon protects your install date for {address}. "
                "Approve ${estimate_amount}? — {owner_name}"
            ),
            day5_email_subject="Order window to protect install date",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "Manufacturer lead times mean early approval helps. Ready to move on "
                "${estimate_amount} for {address}?\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Following up on "
                "windows/doors for {address}. Any product questions before we order?"
            ),
            day10_sms=(
                "Final follow-up from {company} on {address} (${estimate_amount}). "
                "Order or close? — {owner_name}"
            ),
            day10_email_subject="Keep your windows quote active?",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Please advise on the ${estimate_amount} windows/doors estimate for "
                "{address}.\n\n— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Last check on "
                "windows/doors at {address}. Ready to place the order?"
            ),
        ),
    ),
    "fencing": TradeProfile(
        key="fencing",
        label="Fencing",
        emoji="🏡",
        avg_ticket="$2k–$12k",
        pain_point="Neighbor bids are common — persistence closes the yard.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — confirming the fence estimate for "
                "{address} (${estimate_amount}). Questions on materials/HOA? — {owner_name}"
            ),
            day2_email_subject="Fence estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your fencing estimate for {address} is ${estimate_amount}. We can adjust "
                "for material upgrades or gate changes easily.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: crew slot opening near {address}. Want the ${estimate_amount} "
                "fence on the schedule? — {owner_name}"
            ),
            day5_email_subject="Fence crew availability",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "We can schedule your ${estimate_amount} fence project at {address} if "
                "you’re ready. Happy to match a reasonable competitor quote.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Checking on the fence "
                "quote for {address}. Comparing other bids, or ready to book?"
            ),
            day10_sms=(
                "Last note from {company} on {address} fence (${estimate_amount}). "
                "Book or close? — {owner_name}"
            ),
            day10_email_subject="Fence quote — final check",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Should we keep the ${estimate_amount} fencing estimate open for "
                "{address}?\n\n— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final follow-up on the "
                "fence at {address}. Want us to install?"
            ),
        ),
    ),
    "remodeling": TradeProfile(
        key="remodeling",
        label="Remodeling",
        emoji="🛠️",
        avg_ticket="$15k–$150k+",
        pain_point="High-ticket remodels need patient, professional persistence.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — hope you received the remodel proposal "
                "for {address} (${estimate_amount}). Glad to review sections. — {owner_name}"
            ),
            day2_email_subject="Remodel proposal — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Thank you for trusting us with the walkthrough. Your remodel proposal "
                "for {address} totals ${estimate_amount}. I can break down phases, "
                "allowances, and schedule next.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: open to a short design/budget call on {address}? Helps many "
                "homeowners decide on ${estimate_amount}. — {owner_name}"
            ),
            day5_email_subject="Let's refine scope & budget",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "If the ${estimate_amount} remodel for {address} feels heavy, we can "
                "phase kitchen/bath/living areas so you start sooner without overextending.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Following up on the "
                "remodel proposal for {address}. What’s the priority room, and what’s "
                "blocking the yes?"
            ),
            day10_sms=(
                "Final check-in from {company} on {address} (${estimate_amount}). "
                "Proceed, phase, or close? — {owner_name}"
            ),
            day10_email_subject="Remodel proposal decision — {address}",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "I don’t want your project to stall. Tell me if we should proceed, "
                "phase the ${estimate_amount} remodel at {address}, or close the proposal.\n\n"
                "— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final follow-up on the "
                "remodel at {address}. Are we moving forward, phasing, or pausing?"
            ),
        ),
    ),
    "pest_control": TradeProfile(
        key="pest_control",
        label="Pest Control",
        emoji="🐜",
        avg_ticket="$150–$2k",
        pain_point="Urgent when itchy — speed-to-follow-up books the route.",
        sequences=_seq(
            day2_sms=(
                "Hi {homeowner_first}, {company} — checking you got the pest treatment "
                "quote for {address} (${estimate_amount}). Still seeing activity? "
                "— {owner_name}"
            ),
            day2_email_subject="Pest treatment estimate — {address}",
            day2_email=(
                "Hi {homeowner_first},\n\n"
                "Your pest control estimate for {address} is ${estimate_amount}. We can "
                "usually get on-site quickly once approved.\n\n"
                "— {owner_name}\n{company}"
            ),
            day5_sms=(
                "{company}: route day near {address} this week. Approve ${estimate_amount} "
                "and you’re on it. — {owner_name}"
            ),
            day5_email_subject="We can add you to this week's route",
            day5_email=(
                "Hi {homeowner_first},\n\n"
                "We’re servicing your area soon. Approve the ${estimate_amount} treatment "
                "for {address} and we’ll add you to the route.\n\n"
                "— {owner_name}\n{company} | {company_phone}"
            ),
            day5_call=(
                "Hi {homeowner_first}, {owner_name} with {company}. Checking on the pest "
                "quote for {address}. Still dealing with activity? We can treat this week."
            ),
            day10_sms=(
                "Last follow-up — {company} on {address} (${estimate_amount}). Schedule "
                "treatment or close quote? — {owner_name}"
            ),
            day10_email_subject="Pest quote — final check",
            day10_email=(
                "Hi {homeowner_first},\n\n"
                "Should we schedule the ${estimate_amount} treatment for {address} or "
                "close the estimate?\n\n— {owner_name}\n{company}"
            ),
            day10_call=(
                "Hi {homeowner_first}, {owner_name} at {company}. Final check on pest "
                "treatment at {address}. Want us to come out?"
            ),
        ),
    ),
}


PRICING_TIERS = (
    {
        "key": "starter",
        "name": "Starter",
        "price": 500,
        "price_label": "$500/mo",
        "blurb": "Solo operators who send 20–50 estimates a month.",
        "features": [
            "Day 2 / 5 / 10 SMS + email sequences",
            "1 trade playbook",
            "Up to 50 open estimates",
            "Pipeline dashboard",
            "Call scripts on Day 5 & 10",
        ],
    },
    {
        "key": "growth",
        "name": "Growth",
        "price": 997,
        "price_label": "$997/mo",
        "blurb": "Crew-based roofers, painters, and landscapers closing harder.",
        "features": [
            "Everything in Starter",
            "Up to 3 trade playbooks",
            "Up to 200 open estimates",
            "Won/lost reason tracking",
            "Reply detection & pause rules",
            "Monthly close-rate report",
        ],
        "highlighted": True,
    },
    {
        "key": "scale",
        "name": "Scale",
        "price": 1500,
        "price_label": "$1,500/mo",
        "blurb": "Multi-crew construction & home-services companies.",
        "features": [
            "Everything in Growth",
            "Unlimited estimates & trades",
            "Custom sequences per sales rep",
            "Priority onboarding (we load your book)",
            "Twilio + CRM webhook hooks",
            "Quarterly playbook optimization",
        ],
    },
)


def list_trades() -> list[TradeProfile]:
    return list(TRADES.values())


def get_trade(key: str) -> TradeProfile:
    if key not in TRADES:
        raise KeyError(f"Unknown trade: {key}")
    return TRADES[key]


FOLLOW_UP_DAYS = (2, 5, 10)