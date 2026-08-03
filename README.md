# GladGate

**Ask every happy customer. Hold bad reviews before they go public.**

GladGate is a WhatsApp-first review gating system for restaurants, auto repair shops, salons, pharmacies, lodges, clinics, hardware shops, car washes, and similar small businesses — especially in developing markets like Zimbabwe.

Unhappy clients write one-star essays at midnight. GladGate asks the quiet majority while they still feel good, routes praise to Google/Facebook, and flags risky feedback for private recovery.

## Pricing (USD / month)

| Plan | Price | Fit |
| --- | --- | --- |
| Neighborhood | **$500** | 1 location |
| Street Smart | **$900** | Up to 3 locations |
| Citywide | **$1,500** | Up to 10 locations |

Billing designed for USD bank transfer or EcoCash-style collection in Zimbabwe and the region.

## Product flow

1. After a visit, GladGate auto-asks via **WhatsApp** (SMS fallback).
2. Score **4–5** with clean language → one-tap **public review** link.
3. Low scores or complaint / refund / safety language → **held private**, owner alerted, never posted automatically.

## App

```bash
cd gladgate
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

- `/` — marketing site
- `/dashboard` — live demo control room (send asks, watch flags)
- `/feedback/[id]` — customer pulse reply (opened from dashboard)

## Tests

```bash
cd gladgate
npm test
npm run lint
npm run build
```

## Demo script

1. Open `/dashboard`
2. Click **Auto-ask 3 via WhatsApp**
3. Open a customer reply link
4. Try a 5★ clean note → routed public
5. Try a 2★ note with “terrible” / “refund” → flagged private

## Stack

- Next.js (App Router) + TypeScript
- In-memory demo store + review gating engine (`src/lib/engine.ts`)
