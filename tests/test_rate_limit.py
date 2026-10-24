from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

from app.core.limiter import limiter


async def test_login_rate_limited(client, monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(limiter, "_storage", storage)
    monkeypatch.setattr(limiter, "_limiter", FixedWindowRateLimiter(storage))
    monkeypatch.setattr(limiter, "enabled", True)

    form = {"username": "nobody@test.com", "password": "wrong"}

    for _ in range(5):
        r = await client.post("/auth/login", data=form)
        assert r.status_code != 429  # 401 for bad credentials

    blocked = await client.post("/auth/login", data=form)
    assert blocked.status_code == 429
