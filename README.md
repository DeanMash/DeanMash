# Deriv Trade Advisor (suggestions only)

Python tool that connects to your **Deriv** account, reads recent market ticks and trade history, pulls public financial news, then produces **trade suggestions with confidence scores**.

It does **not** place trades.

## Phone access (Telegram)

Best way to use this from your phone:

1. The bot process runs on a computer / always-on machine / VPS
2. You open Telegram on your phone and send `/suggest`
3. Suggestions come back as chat messages

### Telegram setup

1. In Telegram, talk to [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
2. Put it in `.env` as `TELEGRAM_BOT_TOKEN=...`
3. Start the bot:

```bash
python -m deriv_advisor telegram
```

4. Message your bot → `/chatid` → copy the number into `.env`:

```env
TELEGRAM_ALLOWED_CHAT_IDS=123456789
```

5. Restart the bot, then send `/suggest` from your phone

Keep the bot process running while you want phone access.

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
4. (Phone) add Telegram bot token + allowed chat id

Recommended: use a **demo** Deriv token while testing.

## Run

One-shot CLI:

```bash
python -m deriv_advisor
```

Telegram bot (phone):

```bash
python -m deriv_advisor telegram
# or: python -m deriv_advisor.telegram_bot
```

Verbose logs:

```bash
python -m deriv_advisor -v
python -m deriv_advisor -v telegram
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
- Lock the bot with `TELEGRAM_ALLOWED_CHAT_IDS` so strangers cannot use your Deriv connection.
- Keep auto-trading off until you have reviewed many suggestion cycles on demo.

## Next step (later)

Optional: small web dashboard, scheduled Telegram alerts, or gated auto-trade with hard risk limits.
