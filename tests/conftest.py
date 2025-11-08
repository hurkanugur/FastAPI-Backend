import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import JWTSettings, AppSettings
from app.core.database import engine, Base, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Fixture for creating a test client
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# Fixture for setting up and tearing down the test database
@pytest.fixture(scope="module")
def test_db():
    # Set up the test database
    test_db_url = "postgresql://test_user:test_password@localhost/test_db"
    test_engine = create_engine(test_db_url, echo=True)
    Base.metadata.create_all(bind=test_engine)

    # Create a session to interact with the test database
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    yield db  # Provide the session to the test

    # Tear down the test database
    Base.metadata.drop_all(bind=test_engine)
    db.close()

# Fixture for setting up JWT settings for testing
@pytest.fixture(scope="module")
def jwt_settings():
    return JWTSettings(
        secret_key="test_secret_key",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

# Fixture to set app settings for testing
@pytest.fixture(scope="module")
def app_settings():
    return AppSettings(
        app_name="Test App",
        app_env="testing",
        app_port=8000
    )

# Fixture to mock the database interaction, so no actual database is needed for tests
@pytest.fixture
def mock_db_session(mocker, test_db):
    mocker.patch("app.core.database.SessionLocal", return_value=test_db)
    yield test_db
