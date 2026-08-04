# GladGate web app

Next.js demo for GladGate — WhatsApp-first review gating for small businesses.

Run each command on its own line (especially on Windows PowerShell, which rejects `&&` on older versions):

```powershell
npm install
npm run build
npm start
```

Or for hot reload during development:

```powershell
npm install
npm run dev
```

Then open http://localhost:3000

| Script | Purpose |
| --- | --- |
| `npm run dev` | Local app at http://localhost:3000 |
| `npm start` | Production server (after `npm run build`) |
| `npm test` | Review-gate engine tests |
| `npm run lint` | ESLint |
| `npm run build` | Production build |

See the [root README](../README.md) for product positioning and pricing.
