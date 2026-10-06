"""
Reproduction test for B016.
register_user queries for an existing user but never raises HTTPException on duplicate.
The duplicate insert reaches the DB, which raises a UNIQUE constraint error (not HTTP 400).
"""
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.database import Base
from app.services import auth_service
from tests.test_utils import engine, TestingSessionLocal


def test_B016():
    """
    Expected: registering the same email twice raises HTTP 400 on the second call.
    Actual:   the duplicate-email check is silently ignored; the second insert either
              raises SQLAlchemy IntegrityError (DB constraint) or creates a second user.
              Neither is a clean HTTP 400 response.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        auth_service.register_user(db, "b016@test.com", "password1")

        raised_http_400 = False
        raised_integrity_error = False
        try:
            auth_service.register_user(db, "b016@test.com", "password2")
            # If we reach here, a second user was silently created — also a bug
        except HTTPException as exc:
            if exc.status_code == 400:
                raised_http_400 = True
        except IntegrityError:
            raised_integrity_error = True
            # Roll back the failed transaction so the session is usable
            db.rollback()

        # The correct behaviour is HTTP 400. The bug causes IntegrityError or silent success.
        # This assertion FAILS on the buggy codebase (no clean HTTP 400 is raised).
        assert raised_http_400, (
            f"Expected HTTP 400 for duplicate email registration. "
            f"Got: IntegrityError={raised_integrity_error} — "
            f"register_user does not raise HTTPException on duplicate (B016 is active)"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
