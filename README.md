# GladGate by Mashtech

**Register your shop → get a review link + QR → Mashtech posts happy reviews tagging your page.**

For small companies in Zimbabwe and similar markets: **$3 / month on EcoCash**.

## Pre-launch trial codes

| Code | Days | Register link |
| --- | --- | --- |
| `MASHTECH14` | 14 | `/register?code=MASHTECH14` |
| `GLADLAUNCH` | 30 | `/register?code=GLADLAUNCH` |
| `ECOCASH3` | 30 | `/register?code=ECOCASH3` |
| `DEMOQR` | 7 | `/register?code=DEMOQR` |

Or open `/trial` in the app for the full list.

## What you get

1. Company registration
2. Unique review URL + printable QR code
3. Customer registry with automatic WhatsApp/SMS follow-ups
4. Happy reviews queued for **Mashtech** social posting (tags your Facebook page)
5. Bad / risky reviews held private for owner recovery
6. EcoCash **$3 / month** — monthly plan activates **only after Mashtech payment confirmation** (EcoCash webhook)

## Billing flow

1. **Register** → one free trial (14 days, or longer with a trial code)
2. After trial → owner clicks **Request EcoCash payment** on dashboard
3. Shop pays **$3** on EcoCash using the generated **reference** (e.g. `GG-SHOP-ABC123`)
4. Mashtech receives EcoCash confirmation → calls webhook → **monthly plan activated**

Mashtech webhook (server-side only):

```powershell
curl -X POST http://localhost:3000/api/payments/confirm `
  -H "Content-Type: application/json" `
  -H "X-Mashtech-Secret: mashtech-ecocash-demo-secret" `
  -d "{\"reference\":\"GG-YOUR-REFERENCE\"}"
```

Set `ECOCASH_WEBHOOK_SECRET` in production. Shops cannot activate billing themselves — only confirmed payments activate the plan.

## Run on Windows PowerShell (copy each line)

You must **clone the repo first**. Do not type `path\to\...` — that was only an example.

```powershell
cd $HOME
git clone https://github.com/DeanMash/DeanMash.git
cd DeanMash
git checkout cursor/gladgate-review-saas-68cb
cd gladgate
npm install
npm run build
npm start
```

Then open http://localhost:3000 in your browser.

If you already cloned earlier:

```powershell
cd $HOME\DeanMash
git fetch
git checkout cursor/gladgate-review-saas-68cb
git pull
cd gladgate
npm install
npm run build
npm start
```

For hot reload during development, use `npm run dev` instead of `build` + `start`.

## Mashtech dashboard (login required)

Open http://localhost:3000/mashtech/login

Default demo password: `Mashtech2026!` — **change before launch** via `MASHTECH_DASHBOARD_PASSWORD`.

Features:

- **All projects** with **average star rating** per shop
- **Auto-created social posts** — caption + **Download JPG** (1080×1080 JPEG)
- Copy caption · Mark published · Publish all
- Confirm EcoCash payments

Shops register → go to their shop dashboard. Project + launch post appear in Mashtech automatically.

### Useful URLs

- `/mashtech/login` — Mashtech sign-in
- `/mashtech` — control room (after login)
- `/register?code=MASHTECH14` — register a shop
- `/trial` — trial codes
- `/b/amanzi-grill/dashboard` — sample shop dashboard

## Go live on the internet (Vercel)

GladGate lives in the **`gladgate`** folder (Next.js). The repo root is FastAPI — do **not** deploy `./`.

### Exact Vercel settings

| Field | Value |
| --- | --- |
| GitHub repo | `DeanMash/DeanMash` |
| Branch | **`main`** |
| Root Directory | **`gladgate`** (click Edit → open folder → select `gladgate`) |
| Framework Preset | **Next.js** (must appear after you pick `gladgate`) |

If Framework still says **FastAPI**, Root Directory is still `./` — change it to `gladgate` and wait for Vercel to re-detect.

### Env vars (Settings → Environment Variables)

From `gladgate/.env.example`:

- `NEXT_PUBLIC_APP_URL` = your live URL (e.g. `https://gladgate.vercel.app`)
- `MASHTECH_DASHBOARD_PASSWORD` = strong password
- `MASHTECH_SESSION_SECRET` = random string
- `ECOCASH_WEBHOOK_SECRET` = webhook secret

Deploy → open `/mashtech/login` on your live URL.

```powershell
cd gladgate
copy .env.example .env.local
# edit .env.local, then for Vercel paste same values in project Settings → Environment Variables
```

## Tests

```powershell
cd $HOME\DeanMash\gladgate
npm test
npm run lint
npm run build
```
