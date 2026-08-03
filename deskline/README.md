# Deskline

After-hours AI receptionist for **dental surgeries**, **plumbers**, and **med spas**.

When the business closes at 5pm, Deskline answers every call, qualifies the lead with industry-specific questions, and books an appointment in the next working-hours window — so you stop losing the ~85% of callers who never ring back.

## Product

| Plan | Price | Fit |
| --- | --- | --- |
| Frontline | **$1,000 / mo** | Single location |
| Practice | **$1,800 / mo** | Growing practices, custom triage |
| Network | **$3,000 / mo** | Multi-site groups |

## What’s in this app

- Marketing site with brand-first hero, industry stories, and pricing
- Interactive call demo (answer as the caller → qualify → book)
- Booking engine that respects each vertical’s working days/hours
- Lead scoring with `qualified` / `triage` / `callback` outcomes

## Run locally

```bash
cd deskline
npm install
npm run dev
```

Open the URL Vite prints (usually `http://127.0.0.1:5173`).

```bash
npm run build    # production build
npm run preview  # serve the build
npm test         # booking engine tests
```

## Going live (integration path)

Deskline’s demo engine is the same decision layer you’d wire to telephony:

1. **Inbound voice** — Twilio / Vonage / Vapi answers after-hours forwards
2. **Qualify** — industry scripts + scoring (`src/data/industries.ts`, `src/lib/booking.ts`)
3. **Book** — Google Calendar / Outlook / practice management API
4. **Notify** — SMS confirmation to caller + digest to the practice

## Stack

- React + TypeScript + Vite
- Pure client-side qualification/booking logic (easy to lift into an API)
