import json

from app.core import cache
from app.core.cache import balances_key


async def _setup_group(client):
    """Two users, one group, both members. Returns (headers, group_id, user_ids)."""
    ids = []
    for i, name in enumerate(["alice", "bob"], start=1):
        r = await client.post(
            "/auth/register",
            json={
                "name": name,
                "email": f"{name}@test.com",
                "password": "secret123",
                "phone": f"900000000{i}",
            },
        )
        ids.append(r.json()["id"])

    login = await client.post(
        "/auth/login",
        data={"username": "alice@test.com", "password": "secret123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    g = await client.post("/groups", json={"name": "trip"}, headers=headers)
    group_id = g.json()["id"]
    await client.post(
        f"/groups/{group_id}/members",
        json={"email": "bob@test.com"},
        headers=headers,
    )
    return headers, group_id, ids


async def _add_expense(client, headers, group_id, ids):
    return await client.post(
        f"/groups/{group_id}/expenses",
        json={
            "description": "dinner",
            "total_amount": 100.0,
            "paid_by": ids[0],
            "split_type": "equal",
            "participants": ids,
        },
        headers=headers,
    )


async def test_balances_cache_hit(client, fake_redis):
    headers, gid, ids = await _setup_group(client)
    key = balances_key(gid)

    first = await client.get(f"/groups/{gid}/balances", headers=headers)
    assert first.status_code == 200
    assert await fake_redis.exists(key) == 1
    assert 0 < await fake_redis.ttl(key) <= 86400

    # Overwrite the cached value: if the next response shows it,
    # it was served from Redis and not recomputed from Postgres.
    fake_payload = {
        "balances": [{"user_id": ids[0], "net_amount": 777}],
        "suggested_settlements": [],
    }
    await fake_redis.set(key, json.dumps(fake_payload))

    second = await client.get(f"/groups/{gid}/balances", headers=headers)
    assert second.json() == fake_payload


async def test_cache_invalidated_on_expense(client, fake_redis):
    headers, gid, ids = await _setup_group(client)
    key = balances_key(gid)

    await client.get(f"/groups/{gid}/balances", headers=headers)
    assert await fake_redis.exists(key) == 1

    r = await _add_expense(client, headers, gid, ids)
    assert r.status_code == 201  # change if your route returns 200
    assert await fake_redis.exists(key) == 0

    fresh = await client.get(f"/groups/{gid}/balances", headers=headers)
    assert fresh.json()["suggested_settlements"] != []


async def test_cache_invalidated_on_settlement(client, fake_redis):
    headers, gid, ids = await _setup_group(client)
    key = balances_key(gid)
    await _add_expense(client, headers, gid, ids)

    await client.get(f"/groups/{gid}/balances", headers=headers)
    assert await fake_redis.exists(key) == 1

    r = await client.post(
        f"/groups/{gid}/settlements",
        json={"from_user": ids[1], "to_user": ids[0], "amount": 50.0},
        headers=headers,
    )
    assert r.status_code == 201  # change if needed
    assert await fake_redis.exists(key) == 0


class BrokenRedis:
    async def get(self, *args, **kwargs):
        raise ConnectionError("redis down")

    async def set(self, *args, **kwargs):
        raise ConnectionError("redis down")

    async def delete(self, *args, **kwargs):
        raise ConnectionError("redis down")


async def test_fail_open_when_redis_down(client, monkeypatch):
    headers, gid, ids = await _setup_group(client)
    monkeypatch.setattr(cache, "redis_client", BrokenRedis())

    r = await client.get(f"/groups/{gid}/balances", headers=headers)
    assert r.status_code == 200

    e = await _add_expense(client, headers, gid, ids)
    assert e.status_code == 201  # writes still succeed too
