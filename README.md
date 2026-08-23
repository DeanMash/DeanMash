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
6. EcoCash $3 / month activation (demo confirmation until live billing)

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

### Useful URLs

- `/` — marketing
- `/register?code=MASHTECH14` — register with trial
- `/trial` — all trial codes & links
- `/b/amanzi-grill` — sample public review page (QR target)
- `/b/amanzi-grill/dashboard` — sample owner dashboard with QR

## Tests

```powershell
cd $HOME\DeanMash\gladgate
npm test
npm run lint
npm run build
```
