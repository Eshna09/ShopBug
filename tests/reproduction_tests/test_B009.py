"""
Reproduction test for B009.
Orders.jsx initialises its order list with:
    JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
When localStorage is empty, this evaluates to {} (a plain object).
React then calls {}.map(...) which does not exist on an object,
crashing the Orders page with "orders.map is not a function" or similar.

This test mirrors the logic in Python to confirm the type mismatch.
"""
import json


def _parse_orders_buggy(raw_value: str | None) -> object:
    """Replicates the buggy frontend localStorage parse."""
    return json.loads(raw_value or '{}')


def _parse_orders_correct(raw_value: str | None) -> list:
    """Correct implementation uses '[]' as fallback."""
    return json.loads(raw_value or '[]')


def test_B009_empty_storage_returns_object():
    """
    Expected: when localStorage is empty, orders defaults to [] (array).
    Actual:   defaults to {} (object), which has no .map() method → crash.
    """
    result = _parse_orders_buggy(None)
    assert isinstance(result, dict), "Buggy parse should return a dict (object)"
    assert not isinstance(result, list), "Buggy parse must NOT return a list"
    # In JavaScript, {}.map is undefined → TypeError
    # Verify: correct parse always returns a list
    correct = _parse_orders_correct(None)
    assert isinstance(correct, list), "Correct parse must return a list"


def test_B009_populated_storage_still_works():
    """When orders exist in localStorage, parsing works correctly in both versions."""
    stored = json.dumps([{"id": 1, "total_amount": 99.99}])
    result_buggy = _parse_orders_buggy(stored)
    result_correct = _parse_orders_correct(stored)
    # Both return the stored list when real data is present
    assert isinstance(result_buggy, list), "With real data, buggy parse returns list"
    assert isinstance(result_correct, list)
    assert result_buggy[0]["id"] == 1
