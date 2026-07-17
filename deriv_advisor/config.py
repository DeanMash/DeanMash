from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    app_id: str
    api_token: str
    symbols: list[str]
    tick_count: int
    min_confidence: float
    news_api_key: str | None
    ws_url: str
    telegram_bot_token: str | None
    telegram_allowed_chat_ids: set[int]


def load_config() -> Config:
    load_dotenv()

    app_id = os.getenv("DERIV_APP_ID", "1089").strip()
    api_token = os.getenv("DERIV_API_TOKEN", "").strip()
    symbols_raw = os.getenv("DERIV_SYMBOLS", "R_100,R_75,R_50,R_25,R_10")
    symbols = [s.strip() for s in symbols_raw.split(",") if s.strip()]
    tick_count = int(os.getenv("TICK_COUNT", "200"))
    min_confidence = float(os.getenv("MIN_CONFIDENCE", "55"))
    news_api_key = os.getenv("NEWS_API_KEY", "").strip() or None
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or None
    chat_ids_raw = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    telegram_allowed_chat_ids: set[int] = set()
    if chat_ids_raw:
        for part in chat_ids_raw.split(","):
            part = part.strip()
            if not part:
                continue
            telegram_allowed_chat_ids.add(int(part))

    if not api_token:
        raise ValueError(
            "DERIV_API_TOKEN is missing. Copy .env.example to .env and add your "
            "Deriv API token (read scope is enough for suggestions)."
        )
    if not symbols:
        raise ValueError("DERIV_SYMBOLS must include at least one symbol.")
    if tick_count < 50:
        raise ValueError("TICK_COUNT should be at least 50 for meaningful signals.")

    return Config(
        app_id=app_id,
        api_token=api_token,
        symbols=symbols,
        tick_count=tick_count,
        min_confidence=min_confidence,
        news_api_key=news_api_key,
        ws_url=f"wss://ws.derivws.com/websockets/v3?app_id={app_id}",
        telegram_bot_token=telegram_bot_token,
        telegram_allowed_chat_ids=telegram_allowed_chat_ids,
    )