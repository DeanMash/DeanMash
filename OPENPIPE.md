# OpenPipe

Find prospects. Write personalised email. Send at scale.

Built for **insurance brokers**, **financial advisors**, and **B2B services** who need clients but hate cold calling — and don't know where to start with email.

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
- Operator dashboard: `http://127.0.0.1:8090/dashboard`

Optional lock:

```env
OPENPIPE_DASHBOARD_TOKEN=pick-a-secret
OPENPIPE_PORT=8090
OPENPIPE_EMAIL_MODE=demo
```

## CLI

```bash
python -m openpipe seed       # reset demo brokerage (Horizon Cover)
python -m openpipe discover   # find more prospects from the pool
python -m openpipe plan       # rebuild Day 0 / 3 / 7 queue
python -m openpipe run        # send due emails (demo logs only)
python -m openpipe web        # start server (default)
```

## Who it fits

Insurance brokers, financial advisors, B2B service firms, accountants, consultants, commercial real estate, recruiters, law firms, IT/MSPs, and marketing agencies — anyone whose growth depends on starting conversations with busy decision-makers.

## How it works

1. Set your ICP (vertical, niche keywords, city)
2. OpenPipe discovers matching prospects with trigger signals
3. Personalised Day 0 / 3 / 7 email sequences are queued
4. Due messages send automatically (demo mode logs only); replies and meetings stop the sequence
5. Dashboard shows pipeline, queue, and activity

Demo mode never hits a live mailbox — it records sends for operators to review.
