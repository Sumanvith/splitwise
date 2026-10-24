from app.core import cache
from app.database import get_db
from app.main import app


class BrokenRedis:
    async def ping(self):
        raise ConnectionError("redis down")


class BrokenSession:
    async def execute(self, *args, **kwargs):
        raise ConnectionError("db down")


async def broken_get_db():
    yield BrokenSession()


async def test_live(client):
    r = await client.get("/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "alive"}


async def test_ready_ok(client):
    r = await client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["checks"] == {"database": "ok", "redis": "ok"}


async def test_ready_when_redis_down(client, monkeypatch):
    monkeypatch.setattr(cache, "redis_client", BrokenRedis())
    r = await client.get("/health/ready")
    assert r.status_code == 200  # app still works without the cache
    assert r.json()["checks"]["redis"] == "down"


async def test_not_ready_when_db_down(client, monkeypatch):
    monkeypatch.setitem(app.dependency_overrides, get_db, broken_get_db)
    r = await client.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["checks"]["database"] == "down"
