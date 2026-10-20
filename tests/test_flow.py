import itertools
import pytest
from app.services.expense_service import _split_equal

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


async def test_balances_requires_auth(client):
    a = await make_user(client, "A", "a@test.com")
    gid = await make_group(client, a, [])
    r = await client.get(f"/groups/{gid}/balances")
    assert r.status_code == 401, r.text


async def test_login_wrong_password(client):
    a = await make_user(client, "A", "a@test.com")
    login = await client.post("/auth/login", data={"username": 'a@test.com', "password": "password"})
    assert login.status_code == 401, login.text


async def test_register_duplicate_email(client):
    a = await make_user(client, "A", "a@test.com")
    b = await client.post(
        "/auth/register",
        json={"name": "B", "email": "a@test.com",
              "password": "Passw0rd!", "phone": "9111111111"},
    )
    assert b.status_code in (400, 409), b.text


async def test_exact_split_happy_path(client):
    a = await make_user(client, "A", "a@test.com")
    b = await make_user(client, "B", "b@test.com")
    gid = await make_group(client, a, [b])
    payload = {
        "description": "Cab", "total_amount": 100.0, "paid_by": a["id"],
        "split_type": "exact", "shares": [{"user_id": a["id"], "amount": 60.0}, {"user_id": b["id"], "amount": 40.0}]
    }
    r = await client.post(f"/groups/{gid}/expenses", json=payload, headers=a["headers"])
    assert r.status_code in (200, 201), r.text
    r = await client.get(f"/groups/{gid}/balances", headers=a["headers"])
    net = {x["user_id"]: x["net_amount"] for x in r.json()["balances"]}
    assert net[a["id"]] == 4000
    assert net[b["id"]] == -4000
    assert sum(net.values()) == 0


async def test_settlement_updates_balances(client):
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

    # GUESS: request field names from_user / to_user / amount (rupees)
    r = await client.post(
        f"/groups/{gid}/settlements",
        json={"from_user": b["id"], "to_user": a["id"], "amount": 100.0},
        headers=b["headers"],
    )
    assert r.status_code in (200, 201), r.text

    r = await client.get(f"/groups/{gid}/balances", headers=a["headers"])
    net = {x["user_id"]: x["net_amount"] for x in r.json()["balances"]}
    assert net[a["id"]] == 10000
    assert net[b["id"]] == 0
    assert net[c["id"]] == -10000
    assert sum(net.values()) == 0


async def test_non_member_payer_400(client):
    a = await make_user(client, "A", "a@test.com")
    b = await make_user(client, "B", "b@test.com")
    outsider = await make_user(client, "X", "x@test.com")
    gid = await make_group(client, a, [b])

    r = await client.post(
        f"/groups/{gid}/expenses",
        json=equal_payload(outsider["id"], 100.0, [a["id"], b["id"]]),
        headers=a["headers"],
    )
    assert r.status_code == 400, r.text


def _amounts(result):
    if isinstance(result, dict):
        return list(result.values())
    return [r[1] for r in result]


@pytest.mark.parametrize(
    "total, users, expected",
    [
        (9000, [1, 2, 3], [3000, 3000, 3000]),   # divides evenly
        (10000, [1, 2, 3], [3334, 3333, 3333]),  # remainder 1 goes to first
        (100, [1, 2, 3], [34, 33, 33]),          # remainder 1 again
        (5000, [1], [5000]),                     # single participant
        (5000, [1, 2], [2500, 2500]),            # two people
    ],
)
def test_split_equal(total, users, expected):
    amounts = _amounts(_split_equal(total, users))
    assert amounts == expected
    assert sum(amounts) == total


def test_split_equal_even():
    amounts = _amounts(_split_equal(9000, [1, 2, 3]))
    assert amounts == [3000, 3000, 3000]


def test_split_equal_single_participant():
    amounts = _amounts(_split_equal(5000, [1]))
    assert amounts == [5000]


async def test_list_and_get_expense(client):
    a = await make_user(client, "A", "a@test.com")
    b = await make_user(client, "B", "b@test.com")
    gid = await make_group(client, a, [b])

    r = await client.post(
        f"/groups/{gid}/expenses",
        json=equal_payload(a["id"], 100.0, [a["id"], b["id"]]),
        headers=a["headers"],
    )
    assert r.status_code in (200, 201), r.text
    expense_id = r.json()["id"]  # GUESS: response has "id"

    # list
    r = await client.get(f"/groups/{gid}/expenses", headers=a["headers"])
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1  # GUESS: list returned at top level

    # get one
    r = await client.get(f"/groups/{gid}/expenses/{expense_id}", headers=a["headers"])
    assert r.status_code == 200, r.text
    assert r.json()["id"] == expense_id


async def test_equal_split_missing_participants_422(client):
    a = await make_user(client, "A", "a@test.com")
    gid = await make_group(client, a, [])

    payload = {"description": "Dinner", "total_amount": 100.0,
               "paid_by": a["id"], "split_type": "equal"}
    r = await client.post(f"/groups/{gid}/expenses", json=payload, headers=a["headers"])
    assert r.status_code == 422, r.text


async def test_exact_split_missing_shares_422(client):
    a = await make_user(client, "A", "a@test.com")
    gid = await make_group(client, a, [])

    payload = {"description": "Cab", "total_amount": 100.0,
               "paid_by": a["id"], "split_type": "exact"}
    r = await client.post(f"/groups/{gid}/expenses", json=payload, headers=a["headers"])
    assert r.status_code == 422, r.text


async def test_zero_total_amount_422(client):
    a = await make_user(client, "A", "a@test.com")
    gid = await make_group(client, a, [])

    r = await client.post(
        f"/groups/{gid}/expenses",
        json=equal_payload(a["id"], 0, [a["id"]]),
        headers=a["headers"],
    )
    assert r.status_code == 422, r.text  # GUESS: schema rejects amount <= 0


async def test_login_unknown_email_401(client):
    r = await client.post("/auth/login", data={"username": "nobody@test.com", "password": "Passw0rd!"})
    assert r.status_code == 401, r.text


async def test_get_expense_not_found_404(client):
    a = await make_user(client, "A", "a@test.com")
    gid = await make_group(client, a, [])

    r = await client.get(f"/groups/{gid}/expenses/99999", headers=a["headers"])
    assert r.status_code == 404, r.text


async def test_get_expense_from_wrong_group_404(client):
    a = await make_user(client, "A", "a@test.com")
    gid1 = await make_group(client, a, [])
    gid2 = await make_group(client, a, [])

    r = await client.post(
        f"/groups/{gid1}/expenses",
        json=equal_payload(a["id"], 100.0, [a["id"]]),
        headers=a["headers"],
    )
    expense_id = r.json()["id"]

    r = await client.get(f"/groups/{gid2}/expenses/{expense_id}", headers=a["headers"])
    assert r.status_code == 404, r.text


async def test_invalid_token_401(client):
    r = await client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401, r.text


async def test_list_settlements(client):
    a = await make_user(client, "A", "a@test.com")
    b = await make_user(client, "B", "b@test.com")
    gid = await make_group(client, a, [b])

    r = await client.post(
        f"/groups/{gid}/settlements",
        json={"from_user": b["id"], "to_user": a["id"],
              "amount": 50.0},  # GUESS: field names
        headers=b["headers"],
    )
    assert r.status_code in (200, 201), r.text

    r = await client.get(f"/groups/{gid}/settlements", headers=a["headers"])
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1  # GUESS: plain list


async def test_settlement_to_self_422(client):
    a = await make_user(client, "A", "a@test.com")
    gid = await make_group(client, a, [])

    r = await client.post(
        f"/groups/{gid}/settlements",
        json={"from_user": a["id"], "to_user": a["id"], "amount": 10.0},
        headers=a["headers"],
    )
    assert r.status_code == 422, r.text


async def test_settlement_non_member_400(client):
    a = await make_user(client, "A", "a@test.com")
    outsider = await make_user(client, "X", "x@test.com")
    gid = await make_group(client, a, [])

    r = await client.post(
        f"/groups/{gid}/settlements",
        json={"from_user": outsider["id"], "to_user": a["id"], "amount": 10.0},
        headers=a["headers"],
    )
    assert r.status_code == 400, r.text  # GUESS: could be 403 or 404
