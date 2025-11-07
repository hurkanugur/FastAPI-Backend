import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user_model import User
from app.core.security import get_password_hash

# ------------------------------
# Create in-memory SQLite DB
# ------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite in-memory
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ------------------------------
# DB Fixture
# ------------------------------
@pytest.fixture(scope="function")
def db_session():
    """
    Returns a SQLAlchemy session connected to a fresh in-memory DB for each test.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)  # Clean up after test


# ------------------------------
# FastAPI TestClient Fixture
# ------------------------------
@pytest.fixture(scope="function")
def client(db_session):
    """
    Returns a TestClient with the get_db dependency overridden.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


# ------------------------------
# Test User Fixture
# ------------------------------
@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Creates a test user in the database.
    """
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="testuser@example.com",
        hashed_password=hashed_password,
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
