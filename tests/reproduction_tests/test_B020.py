"""
Reproduction test for B020.
register_user stores hashed = password (plaintext) instead of hashing
with bcrypt, so pwd_context.verify() can never match the stored value.
"""
from fastapi import HTTPException
from app.database import Base
from app.models.user import User
from app.services import auth_service
from tests.test_utils import engine, TestingSessionLocal


def test_B020():
    """
    Expected: the stored hashed_password is a bcrypt hash, not the plaintext.
    Actual:   hashed_password == the original password string (plaintext storage).
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        auth_service.register_user(db, "b020@test.com", "plaintextpass")
        user = db.query(User).filter(User.email == "b020@test.com").first()
        assert user is not None
        assert user.hashed_password != "plaintextpass", (
            "Password is stored as plaintext — it should be a bcrypt hash"
        )
        # If it were correctly hashed, verify would succeed
        assert auth_service.pwd_context.verify("plaintextpass", user.hashed_password), (
            "bcrypt.verify should succeed if password was hashed correctly"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
