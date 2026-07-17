from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class _Entry(Generic[T]):
    value: T
    expires_at: float


class TTLCache:
    """Simple thread-safe in-memory TTL cache."""

    def __init__(self) -> None:
        self._data: dict[str, _Entry] = {}
        self._lock = threading.Lock()

    def get(self, key: str):
        now = time.monotonic()
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                self._data.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: T, ttl_seconds: float) -> T:
        if ttl_seconds <= 0:
            return value
        with self._lock:
            self._data[key] = _Entry(value=value, expires_at=time.monotonic() + ttl_seconds)
        return value

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


# Shared process-wide caches.
news_cache = TTLCache()
ticks_cache = TTLCache()
trades_cache = TTLCache()
report_cache = TTLCache()
