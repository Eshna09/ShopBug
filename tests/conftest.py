"""
Shared pytest fixtures for the ShopBug test suite.
The autouse setup_db fixture creates/drops tables around every test and
installs the in-memory SQLite override for the get_db dependency.
"""
import pytest
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from tests.test_utils import engine, TestingSessionLocal, override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
