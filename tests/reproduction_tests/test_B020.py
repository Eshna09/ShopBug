"""Reproduction test for B020 — password stored as plaintext."""
import pytest
from app.database import Base
from app.services import auth_service
from tests.test_utils import engine, TestingSessionLocal


def test_B020():
    """Registering and then logging in with the same password should succeed."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        auth_service.register_user(db, "b020@test.com", "abc123")
        try:
            user = auth_service.login_user(db, "b020@test.com", "abc123")
            assert user is not None, "Expected login to succeed with correct password"
        except HTTPException as exc:
            assert False, f"Login with correct password should succeed, got {exc.status_code}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
