from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

logger = logging.getLogger(__name__)


@dataclass
class AccountInfo:
    loginid: str
    currency: str
    balance: float
    email: str | None
    is_virtual: bool


@dataclass
class TickSeries:
    symbol: str
    prices: list[float]
    epochs: list[int]


@dataclass
class StatementTrade:
    transaction_id: int
    action_type: str
    amount: float
    balance_after: float
    contract_id: int | None
    longcode: str
    symbol: str | None
    transaction_time: int


class DerivClient:
    """Async Deriv WebSocket client for read-only market/account data."""

    def __init__(self, ws_url: str, api_token: str) -> None:
        self.ws_url = ws_url
        self.api_token = api_token
        self._ws: ClientConnection | None = None
        self._req_id = 0
        self.account: AccountInfo | None = None

    async def __aenter__(self) -> DerivClient:
        self._ws = await websockets.connect(self.ws_url, ping_interval=20, ping_timeout=20)
        self.account = await self.authorize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._ws is None:
            raise RuntimeError("WebSocket is not connected")

        req_id = self._next_req_id()
        message = {**payload, "req_id": req_id}
        await self._ws.send(json.dumps(message))

        while True:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=30)
            data = json.loads(raw)
            if data.get("req_id") != req_id:
                # Ignore unrelated subscription pushes.
                continue
            if data.get("error"):
                err = data["error"]
                raise RuntimeError(f"Deriv API error: {err.get('code')} — {err.get('message')}")
            return data

    async def authorize(self) -> AccountInfo:
        data = await self._request({"authorize": self.api_token})
        auth = data["authorize"]
        info = AccountInfo(
            loginid=auth.get("loginid", ""),
            currency=auth.get("currency", ""),
            balance=float(auth.get("balance", 0)),
            email=auth.get("email"),
            is_virtual=bool(auth.get("is_virtual", 0)),
        )
        logger.info(
            "Authorized %s (%s) balance=%.2f %s",
            info.loginid,
            "demo" if info.is_virtual else "real",
            info.balance,
            info.currency,
        )
        return info

    async def get_ticks_history(self, symbol: str, count: int) -> TickSeries:
        data = await self._request(
            {
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": count,
                "end": "latest",
                "style": "ticks",
            }
        )
        history = data["history"]
        prices = [float(p) for p in history.get("prices", [])]
        epochs = [int(e) for e in history.get("times", [])]
        if len(prices) < 2:
            raise RuntimeError(f"Not enough tick history for {symbol}")
        return TickSeries(symbol=symbol, prices=prices, epochs=epochs)

    async def get_recent_trades(self, limit: int = 25) -> list[StatementTrade]:
        data = await self._request(
            {
                "statement": 1,
                "description": 1,
                "limit": limit,
            }
        )
        trades: list[StatementTrade] = []
        for item in data.get("statement", {}).get("transactions", []):
            action = str(item.get("action_type", ""))
            if action not in {"buy", "sell"}:
                continue
            trades.append(
                StatementTrade(
                    transaction_id=int(item.get("transaction_id", 0)),
                    action_type=action,
                    amount=float(item.get("amount", 0)),
                    balance_after=float(item.get("balance_after", 0)),
                    contract_id=item.get("contract_id"),
                    longcode=str(item.get("longcode", "")),
                    symbol=item.get("shortcode") or None,
                    transaction_time=int(item.get("transaction_time", 0)),
                )
            )
        return trades
