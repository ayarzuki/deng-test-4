import psycopg2
import pytest
from fastapi.testclient import TestClient

from app.database import create_tables, set_connection_factory, get_db
from app.main import app

# Test database URL — connects to PostgreSQL on localhost (run via Docker)
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/pokemon_test_db"


def _get_admin_conn():
    """Connect to the default 'postgres' database for admin operations."""
    conn = psycopg2.connect(
        "postgresql://postgres:postgres@localhost:5433/postgres"
    )
    conn.autocommit = True
    return conn


def _create_test_db():
    """Create the test database if it doesn't exist."""
    conn = _get_admin_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = 'pokemon_test_db'"
    )
    if not cursor.fetchone():
        cursor.execute("CREATE DATABASE pokemon_test_db")
    cursor.close()
    conn.close()


def _test_connection():
    """Create a connection to the test database."""
    return psycopg2.connect(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create the test database once per test session."""
    _create_test_db()


@pytest.fixture(scope="function")
def db_connection(setup_test_db):
    """Create a fresh table for each test, drop it after."""
    conn = _test_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS effect_entries")
    conn.commit()
    cursor.close()
    create_tables(conn)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def client(db_connection):
    """FastAPI test client with overridden DB dependency and startup event."""
    set_connection_factory(_test_connection)

    def override_get_db():
        conn = _test_connection()
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db

    # Replace the startup event to no-op for tests
    original_startup_handlers = app.router.on_startup.copy()
    app.router.on_startup.clear()
    app.router.on_startup.append(lambda: None)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    app.router.on_startup.clear()
    app.router.on_startup.extend(original_startup_handlers)
    set_connection_factory(None)
