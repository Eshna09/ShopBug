"""
Reproduction test for B019.

Root cause: app/services/auth_service.py :: login_user (line 23)

    BUG:     if pwd_context.verify(password, user.hashed_password):
                 raise HTTPException(401, ...)
    CORRECT: if not pwd_context.verify(password, user.hashed_password):
                 raise HTTPException(401, ...)

The missing `not` inverts the condition so HTTP 401 is raised when the
password IS correct, and login succeeds when the password is WRONG.

Isolation strategy
------------------
B020 (register_user stores plaintext) means bcrypt.verify() raises
UnknownHashError before B019's branch can ever execute — the two bugs
compound at runtime. To isolate B019 cleanly we bypass register_user
entirely and insert a user whose hashed_password is a REAL bcrypt hash
produced directly by pwd_context.hash(). This lets verify() complete
and exposes B019's inverted logic without interference from B020.

test_B019_source_check  — static: confirms the inverted pattern exists
                          in the source (no `not` before verify).
test_B019_correct_password_raises_401 — runtime, B019 isolated:
    a correctly hashed password is in the DB; login with the CORRECT
    password should succeed but raises HTTP 401 (inversion active).
test_B019_wrong_password_succeeds — runtime, B019 isolated:
    login with an INCORRECT password should raise 401 but instead
    returns the user object (inversion active).
"""
import re
from pathlib import Path

from fastapi import HTTPException

from app.database import Base
from app.models.user import User
from app.services import auth_service
from tests.test_utils import engine, TestingSessionLocal

AUTH_SERVICE = (
    Path(__file__).resolve().parents[2] / "app" / "services" / "auth_service.py"
)


# ---------------------------------------------------------------------------
# Static check
# ---------------------------------------------------------------------------

def test_B019_source_check():
    """
    Confirm the inverted condition is present in the source.

    On the BUGGY codebase  → PASSES  (pattern without `not` found).
    On a FIXED codebase    → FAILS   (`not` is present).
    """
    assert AUTH_SERVICE.exists(), f"auth_service.py not found at {AUTH_SERVICE}"
    src = AUTH_SERVICE.read_text(encoding="utf-8")

    inverted = re.search(r"if pwd_context\.verify\(password", src)
    correct  = re.search(r"if not pwd_context\.verify\(password", src)

    assert inverted and not correct, (
        "B019 not detected: expected `if pwd_context.verify(password` "
        "(inverted, no `not`) but the correct form `if not pwd_context.verify` "
        "was found instead."
    )


# ---------------------------------------------------------------------------
# Helper: insert a user with a REAL bcrypt hash, bypassing register_user.
# This isolates B019 from B020 (plaintext storage).
# ---------------------------------------------------------------------------

def _insert_hashed_user(db, email: str, plaintext: str) -> User:
    """
    Write a user whose hashed_password is a genuine bcrypt hash produced by
    pwd_context.hash().  Does NOT go through register_user, so B020 cannot
    interfere with the hash stored in the DB.
    """
    real_hash = auth_service.pwd_context.hash(plaintext)
    user = User(email=email, hashed_password=real_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Runtime checks — B019 isolated
# ---------------------------------------------------------------------------

def test_B019_correct_password_raises_401():
    """
    Expected: login with the CORRECT password succeeds (returns the user).
    Actual:   HTTP 401 is raised because the inverted condition fires when
              verify() returns True.

    On the BUGGY codebase  → FAILS  (401 is raised instead of success).
    On a FIXED codebase    → PASSES (user is returned).
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        _insert_hashed_user(db, "b019_correct@test.com", "correctpass")

        try:
            user = auth_service.login_user(db, "b019_correct@test.com", "correctpass")
            # Reached only if the bug is FIXED — correct behaviour
            assert user is not None, "Expected login to return a user"
        except HTTPException as exc:
            # On the buggy codebase verify(correct)==True triggers the raise
            assert False, (
                f"Login with correct password raised HTTP {exc.status_code} — "
                "B019 inverted condition is active: verify() succeeded but "
                "the condition raised 401 instead of allowing login."
            )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_B019_wrong_password_succeeds():
    """
    Expected: login with a WRONG password raises HTTP 401.
    Actual:   login succeeds (user returned) because verify() returns False,
              making the inverted `if verify():` condition False — so the
              raise is skipped and login proceeds.

    On the BUGGY codebase  → FAILS  (login succeeds with wrong password).
    On a FIXED codebase    → PASSES (401 raised for wrong password).
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        _insert_hashed_user(db, "b019_wrong@test.com", "correctpass")

        try:
            user = auth_service.login_user(db, "b019_wrong@test.com", "wrongpass")
            # On the buggy codebase verify(wrong)==False → condition is False
            # → raise is skipped → login "succeeds" (returns user)
            assert False, (
                "Login with WRONG password returned a user — B019 inverted "
                "condition skipped the 401 raise because verify() was False."
            )
        except HTTPException as exc:
            # Expected correct behaviour: wrong password → 401
            assert exc.status_code == 401, (
                f"Expected HTTP 401 for wrong password, got {exc.status_code}"
            )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
