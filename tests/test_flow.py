import itertools

_phone_counter = itertools.count(9000000000)


async def make_user(client, name, email, password="Passw0rd!"):
    r = await client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password,
              "phone": str(next(_phone_counter))},
    )
    assert r.status_code in (200, 201), r.text
    r = await client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    me = await client.get("/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    return {"id": me.json()["id"], "email": email, "headers": headers}


async def make_group(client, owner, members):
    r = await client.post("/groups", json={"name": "Trip"}, headers=owner["headers"])
    assert r.status_code in (200, 201), r.text
    group_id = r.json()["id"]
    for m in members:
        r = await client.post(f"/groups/{group_id}/members", json={"email": m["email"]}, headers=owner["headers"])
        assert r.status_code in (200, 201), r.text
    return group_id


def equal_payload(payer_id, amount, participants):
    return {
        "description": "Dinner", "total_amount": amount, "paid_by": payer_id,
        "split_type": "equal", "participants": participants,  # GUESS: list of user ids
    }


async def test_equal_expense_then_balances(client):
    a = await make_user(client, "A", "a@test.com")
    b = await make_user(client, "B", "b@test.com")
    c = await make_user(client, "C", "c@test.com")
    gid = await make_group(client, a, [b, c])

    r = await client.post(
        f"/groups/{gid}/expenses",
        json=equal_payload(a["id"], 300.0, [a["id"], b["id"], c["id"]]),
        headers=a["headers"],
    )
    assert r.status_code in (200, 201), r.text

    r = await client.get(f"/groups/{gid}/balances", headers=a["headers"])
    assert r.status_code == 200, r.text
    print(r.json())
    net = {x["user_id"]: x["net_amount"] for x in r.json()["balances"]}
    assert net[a["id"]] == 20000
    assert net[b["id"]] == -10000
    assert net[c["id"]] == -10000
    assert sum(net.values()) == 0


async def test_exact_split_sum_mismatch_400(client):
    a = await make_user(client, "A", "a@test.com")
    b = await make_user(client, "B", "b@test.com")
    gid = await make_group(client, a, [b])

    payload = {
        "description": "Cab", "total_amount": 100.0, "paid_by": a["id"], "split_type": "exact",
        # GUESS
        "shares": [{"user_id": a["id"], "amount": 40.0}, {"user_id": b["id"], "amount": 40.0}],
    }
    r = await client.post(f"/groups/{gid}/expenses", json=payload, headers=a["headers"])
    assert r.status_code == 400, r.text


async def test_non_member_forbidden_403(client):
    a = await make_user(client, "A", "a@test.com")
    outsider = await make_user(client, "X", "x@test.com")
    gid = await make_group(client, a, [])

    r = await client.post(
        f"/groups/{gid}/expenses",
        json=equal_payload(a["id"], 300.0, [a["id"]]),
        headers=outsider["headers"],
    )
    assert r.status_code == 403, r.text
