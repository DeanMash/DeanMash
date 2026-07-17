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
    """Async Deriv WebSocket client with concurrent request support."""

    def __init__(self, ws_url: str, api_token: str) -> None:
        self.ws_url = ws_url
        self.api_token = api_token
        self._ws: ClientConnection | None = None
        self._req_id = 0
        self.account: AccountInfo | None = None
        self._pending: dict[int, asyncio.Future] = {}
        self._listener_task: asyncio.Task | None = None

    async def __aenter__(self) -> DerivClient:
        self._ws = await websockets.connect(self.ws_url, ping_interval=20, ping_timeout=20)
        self._listener_task = asyncio.create_task(self._listen(), name="deriv-ws-listener")
        self.account = await self.authorize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._listener_task is not None:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None

        for fut in list(self._pending.values()):
            if not fut.done():
                fut.cancel()
        self._pending.clear()

        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _listen(self) -> None:
        assert self._ws is not None
        try:
            async for raw in self._ws:
                data = json.loads(raw)
                req_id = data.get("req_id")
                fut = self._pending.get(req_id)
                if fut is None or fut.done():
                    continue
                if data.get("error"):
                    err = data["error"]
                    fut.set_exception(
                        RuntimeError(f"Deriv API error: {err.get('code')} — {err.get('message')}")
                    )
                else:
                    fut.set_result(data)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Deriv WebSocket listener stopped")
            for fut in list(self._pending.values()):
                if not fut.done():
                    fut.set_exception(exc)

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._ws is None:
            raise RuntimeError("WebSocket is not connected")

        req_id = self._next_req_id()
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[req_id] = fut
        try:
            await self._ws.send(json.dumps({**payload, "req_id": req_id}))
            return await asyncio.wait_for(fut, timeout=30)
        finally:
            self._pending.pop(req_id, None)

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
