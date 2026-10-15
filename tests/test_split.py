from app.services.expense_service import _split_equal  # GUESS: module-level function


def test_split_equal_remainder_goes_to_first():
    # GUESS: signature (total_paise, user_ids) -> list of (user_id, paise) or dict
    result = _split_equal(10000, [1, 2, 3])
    amounts = [r[1] for r in result] if isinstance(result, list) else list(result.values())
    assert amounts == [3334, 3333, 3333]
    assert sum(amounts) == 10000