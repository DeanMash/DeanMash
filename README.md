# Deriv Trade Advisor (suggestions only)

Python CLI that connects to your **Deriv** account, reads recent market ticks and trade history, pulls public financial news, then prints **trade suggestions with confidence scores**.

It does **not** place trades.

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

Recommended: use a **demo** token while testing.

## Run

```bash
python -m deriv_advisor
```

Verbose logs:

```bash
python -m deriv_advisor -v
```

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
- Keep auto-trading off until you have reviewed many suggestion cycles on demo.

## Next step (later)

When you want automation, we can add a separate gated executor that only trades above a high confidence threshold with hard risk limits — still disabled by default.
