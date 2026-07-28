from deriv_advisor.cache import TTLCache


def test_ttl_cache_expires(monkeypatch):
    cache = TTLCache()
    cache.set("a", 123, ttl_seconds=10)
    assert cache.get("a") == 123

    # Expire by moving monotonic clock forward.
    real_monotonic = __import__("time").monotonic
    monkeypatch.setattr("deriv_advisor.cache.time.monotonic", lambda: real_monotonic() + 20)
    assert cache.get("a") is None


def test_ttl_cache_disabled_when_zero():
    cache = TTLCache()
    cache.set("b", "x", ttl_seconds=0)
    assert cache.get("b") is None
