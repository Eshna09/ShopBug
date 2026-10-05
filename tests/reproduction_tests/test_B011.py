"""Reproduction test for B011 — duplicate user registration not blocked."""
import pytest
from app.database import Base
from app.services import auth_service
from tests.test_utils import engine, TestingSessionLocal


def test_B011():
    """Registering same email twice should raise HTTP 400."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        auth_service.register_user(db, "b011@test.com", "pass1")
        try:
            auth_service.register_user(db, "b011@test.com", "pass2")
            assert False, "Expected HTTP 400 for duplicate email"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
