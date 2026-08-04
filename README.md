# CloseLoop

**The follow-up system for contractors who already earned the job — then lost it to silence.**

A contractor drives to a homeowner’s house, spends 45 minutes quoting, sends the estimate… and never follows up. The homeowner goes with whoever calls back.

CloseLoop schedules **Day 2**, **Day 5**, and **Day 10** SMS, email, and call scripts automatically so roofers, painters, landscapers, construction crews, and related trades close more of the jobs they already quoted.

## Who it’s for

| Trade | Why follow-up wins |
| --- | --- |
| Roofing | 3 bids → first persistent callback often wins |
| Painting | Protects margin vs cheap silent competitors |
| Landscaping | Seasonal windows close fast |
| General construction | Long cycles die without a chase |
| HVAC / Plumbing / Electrical | Urgency fades unless someone checks in |
| Flooring · Concrete · Windows · Fencing · Remodeling · Pest | Vertical playbooks included |

## Pricing ($500 – $1,500 / mo)

| Plan | Price | Best for |
| --- | --- | --- |
| **Starter** | **$500/mo** | Solo operators, ~50 open estimates, 1 trade playbook |
| **Growth** | **$997/mo** | Crews closing harder — 3 trades, 200 estimates, reports |
| **Scale** | **$1,500/mo** | Multi-crew shops — unlimited, custom sequences, onboarding |

One saved mid-ticket roof or remodel pays for months of software.

## Features

- Log an estimate in ~30 seconds after the site visit
- Auto Day **2 / 5 / 10** sequences (SMS + email)
- Day 5 & Day 10 **call scripts** on the dashboard
- Trade-specific copy (not generic CRM spam)
- Mark **won / lost / paused** — pending follow-ups stop
- Pipeline value, close rate, and outbound message log
- Optional Twilio SMS + SMTP email (logs only until configured)

## Quick start

You must run these commands **inside the project folder** (the folder that contains `requirements.txt` and `closeloop/`).  
If you are in `C:\Users\...` alone, Python cannot find the app.

### 1) Get the code

```powershell
cd $HOME
git clone https://github.com/DeanMash/DeanMash.git CloseLoop
cd CloseLoop
git checkout cursor/contractor-closeloop-followup
```

Or download the ZIP from GitHub → Extract → open that folder in PowerShell with:

```powershell
cd path\to\DeanMash
```

Confirm you are in the right place:

```powershell
dir requirements.txt
dir closeloop
```

### 2) Windows (PowerShell)

Type **only** the lines below — do **not** paste `PS C:\...>` prompts or error messages.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m closeloop web
```

If activation is blocked, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try `.\.venv\Scripts\Activate.ps1` again.

### 3) Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m closeloop web
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

- Marketing + pricing: `/`
- Onboard a company: `/onboard`
- Ops dashboard: `/dashboard`
- Log a quote: `/estimates/new`

Demo data (Summit Shield Roofing) seeds automatically when `SEED_DEMO=true`.

### Process due follow-ups once (CLI)

```bash
python -m closeloop run-followups
```

The web app also runs this on a 15-minute scheduler, and the dashboard has a **Run due follow-ups now** button.

## Configure real SMS / email

Edit `.env`:

```env
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1...

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=followups@yourdomain.com
```

Without these, messages are **logged** (safe for demos) instead of sent.

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

## Product story (pitch)

> You already did the hard part — drove out, measured, earned trust, sent the number.
> CloseLoop makes sure you’re the contractor who calls back on Day 2, Day 5, and Day 10
> so the job doesn’t quietly walk to someone else.

## Note on this repo

This repository also contains an older `deriv_advisor` experiment. **CloseLoop** (`closeloop/`) is the active product.