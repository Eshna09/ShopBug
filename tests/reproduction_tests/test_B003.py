"""Reproduction test for B003 — reversed password verification condition."""
import pytest
from app.database import Base
from app.services import auth_service
from tests.test_utils import engine, TestingSessionLocal


def test_B003():
    """Login with wrong password should fail (401), not succeed."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        auth_service.register_user(db, "b003@test.com", "correctpass")
        try:
            auth_service.login_user(db, "b003@test.com", "wrongpass")
            assert False, "Expected login with wrong password to fail"
        except HTTPException as exc:
            assert exc.status_code == 401, f"Expected 401, got {exc.status_code}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
