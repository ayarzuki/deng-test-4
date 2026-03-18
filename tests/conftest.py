import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Use SQLite in-memory for testing (no PostgreSQL needed)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test client with overridden DB dependency and startup event."""
    app.dependency_overrides[get_db] = override_get_db

    # Replace the startup event to use test engine instead of production engine
    original_startup_handlers = app.router.on_startup.copy()
    app.router.on_startup.clear()
    app.router.on_startup.append(
        lambda: Base.metadata.create_all(bind=test_engine)
    )

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    app.router.on_startup.clear()
    app.router.on_startup.extend(original_startup_handlers)
