# CloseLoop

**Potential clients click a link → register their company → add clients → WhatsApp + email follow-ups run automatically.**

A contractor drives to a homeowner’s house, spends 45 minutes quoting, sends the estimate… and never follows up. The homeowner goes with whoever calls back.

CloseLoop gives you a **public registration link**, a company dashboard, and automatic **WhatsApp + email** chases on **Day 0** (welcome), **Day 2**, **Day 5**, and **Day 10**.

## Client journey (share this)

1. Click the signup link (`/register`)
2. Register the company (name, trade, email, password, plan)
3. Add a client after each estimate (WhatsApp number + email + amount)
4. Follow-ups start automatically
5. Mark won / lost when the job decides

Full write-up inside the app: **`/guide`**  
Social + catalogue advert pack: **`/advertise`**

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

## Features

- Public **Register company** link for ads / catalogues / social
- Login per company account
- Add clients/estimates in ~30 seconds after the site visit
- Auto **WhatsApp + email** on Day 0 / 2 / 5 / 10
- Day 5 & Day 10 **call scripts** on the dashboard
- Trade-specific copy
- Mark **won / lost / paused** — pending follow-ups stop
- Step-by-step guide + advert/catalogue copy pages
- Optional Twilio WhatsApp + SMTP email (logs only until configured)

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

Confirm:

```powershell
dir requirements.txt
dir closeloop
```

### 2) Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# If you ran an older build, reset the DB once:
# Remove-Item closeloop.db -ErrorAction SilentlyContinue
python -m closeloop web
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3) Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# rm -f closeloop.db   # only if upgrading from an older schema
python -m closeloop web
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

| Page | URL |
| --- | --- |
| Landing | `/` |
| **Public company registration** | **`/register`** (also `/start`) |
| Step-by-step guide | `/guide` |
| Social + catalogue ads | `/advertise` |
| Login | `/login` |
| Dashboard | `/dashboard` |
| Add client | `/estimates/new` |

Demo login (when `SEED_DEMO=true`): `demo@closeloop.local` / `demo1234`

### Process due follow-ups once (CLI)

```bash
python -m closeloop run-followups
```

The web app also runs this every 15 minutes, and the dashboard has **Run due follow-ups now**. Saving a new client also fires any due messages immediately (including Day 0 welcome).

## Configure WhatsApp + email

Edit `.env`:

```env
APP_BASE_URL=https://your-domain.com

TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=followups@yourdomain.com
```

Without these, messages are **logged** (safe for demos) instead of sent.

Put your live registration link on posters:

`https://your-domain.com/register`

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

## Note on this repo

Older `deriv_advisor` code may still exist. **CloseLoop** (`closeloop/`) is the active product.