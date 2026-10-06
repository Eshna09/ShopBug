"""
Reproduction test for B005.
api.js checkoutApi.checkout sends user_id and discount_id as a JSON request
body instead of query parameters.  The FastAPI checkout endpoint declares
both as Query parameters, so it never receives the body values and uses
its own defaults (user_id has no default → 422 Unprocessable Entity).

This test confirms the backend rejects a POST /checkout/ with body params.
"""
import pytest
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from tests.test_utils import engine, TestingSessionLocal, override_get_db


def make_client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app, raise_server_exceptions=False)


def test_B005():
    """
    Expected: POST /checkout/?user_id=1 (query param) → processes checkout.
    Actual:   POST /checkout/ with body {"user_id": 1} → 422 because
              user_id is not present in the query string.
    """
    Base.metadata.create_all(bind=engine)
    client = make_client()
    try:
        # Send user_id as body (the buggy frontend behaviour)
        resp_body = client.post(
            "/checkout/",
            json={"user_id": 1, "discount_id": None},
        )
        # Backend reads user_id from query params only → 422
        assert resp_body.status_code == 422, (
            f"Expected 422 when user_id sent as body (frontend bug), "
            f"got {resp_body.status_code}"
        )

        # Confirm that query-param form works (correct behaviour)
        resp_query = client.post("/checkout/", params={"user_id": 1})
        # May get 400 due to empty-cart (B010) but NOT 422
        assert resp_query.status_code != 422, (
            "Query-param checkout should not return 422"
        )
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
