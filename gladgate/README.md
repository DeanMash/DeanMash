# GladGate web app (Mashtech)

## First-time setup on Windows PowerShell

Copy **each line** (do not use `path\to\...`):

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

Open http://localhost:3000

| Path | Purpose |
| --- | --- |
| `/register?code=MASHTECH14` | Register shop with trial |
| `/trial` | Pre-launch codes & links |
| `/b/[slug]` | Public review page (QR target) |
| `/b/[slug]/dashboard` | Owner dashboard: QR, customers, Mashtech queue |
| `/mashtech/login` | Mashtech sign-in (password required) |
| `/mashtech` | Mashtech control room: all shops, JPG posts, avg ratings |

| Script | Purpose |
| --- | --- |
| `npm run dev` | Hot reload |
| `npm start` | Production (after build) |
| `npm test` | Engine + trial + Mashtech tests |
| `npm run lint` | ESLint |
| `npm run build` | Production build |

Default Mashtech password (change before launch): `Mashtech2026!` via `MASHTECH_DASHBOARD_PASSWORD` in `.env.local`.

See the [root README](../README.md) for EcoCash pricing, trial codes, and **Vercel go-live steps**.
