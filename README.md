# DeanMash products

## OpenPipe (prospecting + email outbound)

Find prospects, write personalised emails, and send at scale — for insurance brokers, financial advisors, and B2B services. See [OPENPIPE.md](OPENPIPE.md).

```bash
pip install -r requirements.txt
python -m openpipe
```

- Site: `http://127.0.0.1:8090/`
- Dashboard: `http://127.0.0.1:8090/dashboard`

---

# Deriv Trade Advisor (suggestions only)

Python tool that connects to your **Deriv** account, reads recent market ticks and trade history, pulls public financial news, then produces **trade suggestions with confidence scores**.

It does **not** place trades.

## Phone / browser access

You can use either:

1. **Web dashboard** — open in your phone browser
2. **Telegram bot** — get suggestions as chat messages

Both need the Python process running on a computer / VPS.

### Web dashboard

```bash
python -m deriv_advisor web
```

Then open:

- This computer: `http://127.0.0.1:8000`
- Phone on the same Wi‑Fi: `http://<your-computer-ip>:8000`

Optional lock in `.env`:

```env
DASHBOARD_TOKEN=pick-a-secret
```

Enter that secret in the dashboard **Access token** field before clicking **Get suggestions**.

### Telegram bot

1. Talk to [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
2. Put it in `.env` as `TELEGRAM_BOT_TOKEN=...`
3. Start:

```bash
python -m deriv_advisor telegram
```

4. Message your bot → `/chatid` → set `TELEGRAM_ALLOWED_CHAT_IDS`
5. Send `/suggest` from your phone

## What it uses

| Input | Source |
| --- | --- |
| Account balance + recent trades | Deriv WebSocket API |
| Live tick history | Deriv `ticks_history` |
| News headlines | Free RSS feeds (optional NewsAPI key) |
| Signals | RSI, SMA crossover, short-term momentum + light news/history nudges |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

1. Create an app / note an `app_id` at [developers.deriv.com](https://developers.deriv.com/)
2. Create an API token in your Deriv account (read access is enough)
3. Put both values in `.env`
4. Optional: Telegram + dashboard token settings

Recommended: use a **demo** Deriv token while testing.

## Run

```bash
python -m deriv_advisor            # one-shot CLI
python -m deriv_advisor web        # web dashboard
python -m deriv_advisor telegram   # Telegram bot
```

Verbose:

```bash
python -m deriv_advisor -v web
```

## Bot commands

| Command | Action |
| --- | --- |
| `/start` | Help / welcome |
| `/suggest` | Analyze and send ideas |
| `/ideas` | Same as `/suggest` |
| `/chatid` | Show your Telegram chat id |

## Output

- Account snapshot (demo/real, balance)
- News tone summary + sample headlines
- Ranked suggestions like `R_100 → CALL | confidence 72.5%`
- Reasons for each suggestion

Only ideas above `MIN_CONFIDENCE` (default `55`) are shown.

## Tests

```bash
pip install pytest
pytest -q
```

## Important

- Suggestions are heuristics, not financial advice.
- Synthetic indices are not driven by news the way FX/stocks are; news only applies a small confidence nudge.
- Set `DASHBOARD_TOKEN` and `TELEGRAM_ALLOWED_CHAT_IDS` so strangers cannot use your Deriv connection.
- Keep auto-trading off until you have reviewed many suggestion cycles on demo.

## Next step (later)

Optional: scheduled alerts, or gated auto-trade with hard risk limits.
