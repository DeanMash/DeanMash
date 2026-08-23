# OpenPipe

Find prospects. Write personalised **email + WhatsApp**. Send at scale.

Built for **small organisations** — insurance brokers, financial advisors, and B2B services — who need clients but hate cold calling.

**Pricing:** Starter **$900**/mo · Pipeline **$1,500**/mo · Scale **$2,500**/mo

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m openpipe
```

Open:

- Marketing site: `http://127.0.0.1:8090/`
- **Register:** `http://127.0.0.1:8090/register`
- Operator dashboard: `http://127.0.0.1:8090/dashboard`

Optional env:

```env
OPENPIPE_DASHBOARD_TOKEN=pick-a-secret
OPENPIPE_PORT=8090
OPENPIPE_EMAIL_MODE=demo
OPENPIPE_AUTO_RUN=1
OPENPIPE_AUTO_RUN_INTERVAL=60
```

## Register a small organisation

1. Open `/register`
2. Enter your firm, vertical, email, WhatsApp number, and channel mix (email / WhatsApp / both)
3. Save the **access token** shown after signup
4. Open the dashboard, paste the token, find prospects, preview, send

Registered orgs with **auto-send On** have due messages sent in the background (demo mode logs only).

## CLI

```bash
python -m openpipe seed       # reset demo kits
python -m openpipe discover   # find more prospects
python -m openpipe plan       # rebuild Day 0 / 3 / 7 queue
python -m openpipe run        # send due email + WhatsApp (demo logs)
python -m openpipe web        # start server (default)
```

## Channel mix (`both`)

| Day | Channel |
| --- | --- |
| 0 | Email (first touch) |
| 3 | WhatsApp bump (email if no phone) |
| 7 | Email + WhatsApp soft close |

## Who it fits

Insurance brokers, financial advisors, B2B service firms, accountants, consultants, commercial real estate, recruiters, law firms, IT/MSPs, and marketing agencies.

## How it works

1. Register your organisation (or try a demo ICP kit)
2. OpenPipe discovers matching prospects with trigger signals + phone numbers
3. Personalised Day 0 / 3 / 7 email and WhatsApp sequences are queued
4. Due messages send on click or via auto-run; replies and meetings stop the sequence
5. Dashboard shows pipeline, queue, email/WhatsApp stats

Demo mode never hits a live mailbox or WhatsApp API — it records sends for review.
