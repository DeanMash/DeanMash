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

### Scheduled high-confidence alerts

With the Telegram bot running, it checks markets on a timer and messages you only when confidence is high enough:

```env
ALERT_ENABLED=true
ALERT_INTERVAL_MINUTES=15
ALERT_MIN_CONFIDENCE=70
ALERT_COOLDOWN_MINUTES=30
TELEGRAM_ALLOWED_CHAT_IDS=123456789
```

In Telegram:

- `/alerts` — show settings
- `/alerts on` / `/alerts off` — toggle while running

## Performance

- **Parallel tick fetch** — symbols are requested concurrently over one Deriv WebSocket
- **TTL cache** — news/ticks/trades/full reports reuse results for `CACHE_TTL_SECONDS` (default 45)
- Instagram fetch runs only when links are provided

## Instagram links

Paste public Instagram **post/reel** links in:

- Web dashboard → **Instagram links** box → **Get suggestions**
- Telegram → paste a link, or `/suggest https://www.instagram.com/reel/...`

The system reads available caption/link-preview text and uses it as a **small confidence nudge** (not the main trade trigger).

Notes:

- Public posts work best. Private/login-walled posts often expose no caption.
- For more reliable captions, add a Facebook app token as `FACEBOOK_ACCESS_TOKEN` (Instagram oEmbed).
- Reel audio/video is not transcribed yet — caption text only for now.

### Indices / markets

The dashboard now shows **All watched indices** (CALL / PUT / HOLD) plus **Top ideas**.

Pick indices in the UI, or set them in `.env`:

```env
DERIV_SYMBOLS=R_75,R_100,BOOM1000,CRASH1000,JD50,1HZ75V
```

Common codes: `R_10`…`R_100`, `1HZ75V`, `BOOM1000`, `CRASH1000`, `JD10`…`JD100`.

## What it uses

| Input | Source |
| --- | --- |
| Account balance + recent trades | Deriv WebSocket API |
| Live tick history | Deriv `ticks_history` |
| News headlines | Free RSS feeds (optional NewsAPI key) |
| Instagram captions | Pasted post/reel links (OG preview or oEmbed) |
| Signals | RSI, SMA crossover, short-term momentum + news/Instagram/history nudges |

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
python -m deriv_advisor web        # web dashboard (live Deriv)
python -m deriv_advisor web --demo # sample UI with no Deriv token
python -m deriv_advisor telegram   # Telegram bot
```

### Demo (no API token)

```bash
python -m deriv_advisor web --demo
```

Open `http://127.0.0.1:8000` and click **Get suggestions** to see sample ideas.
Verbose:

```bash
python -m deriv_advisor -v web
```

## Bot commands

| Command | Action |
| --- | --- |
| `/start` | Help / welcome |
| `/suggest` | Analyze and send ideas |
| `/suggest <instagram link>` | Analyze with Instagram caption tone |
| `/ideas` | Same as `/suggest` |
| `/alerts` | Show scheduled alert settings |
| `/alerts on\|off` | Enable/disable scheduled alerts |
| `/chatid` | Show your Telegram chat id |

Paste a bare Instagram link in chat to run analysis with that post/reel.

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

Optional: suggestion outcome tracking, or gated auto-trade with hard risk limits.
