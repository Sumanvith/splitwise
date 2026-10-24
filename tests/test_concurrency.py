import asyncio
from tests.test_cache import _setup_group
from app.repositories import group_repo

async def test_add_member_concurrent_duplicate(client):
    headers, gid, _ = await _setup_group(client)
    await client.post(
        "/auth/register",
        json={
            "name": "carol",
            "email": "carol@test.com",
            "password": "secret123",
            "phone": "9000000003",
        },
    )

    url = f"/groups/{gid}/members"
    body = {"email": "carol@test.com"}
    results = await asyncio.gather(
        client.post(url, json=body, headers=headers),
        client.post(url, json=body, headers=headers),
    )

    codes = sorted(r.status_code for r in results)
    assert codes == [201, 409]  # change 201 if your route returns 200


async def test_add_member_integrity_race(client, monkeypatch):
    headers, gid, ids = await _setup_group(client)  # bob is already a member
    real_get_member = group_repo.get_member

    async def fake_get_member(db, group_id, user_id):
        if user_id == ids[1]:  # pretend bob isn't a member yet
            return None
        return await real_get_member(db, group_id, user_id)

    monkeypatch.setattr(group_repo, "get_member", fake_get_member)

    r = await client.post(
        f"/groups/{gid}/members",
        json={"email": "bob@test.com"},
        headers=headers,
    )
    assert r.status_code == 409

async def test_add_member_twice_conflict(client):
    headers, gid, _ = await _setup_group(client)
    r = await client.post(
        f"/groups/{gid}/members",
        json={"email": "bob@test.com"},
        headers=headers,
    )
    assert r.status_code == 409