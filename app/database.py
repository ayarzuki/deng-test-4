import psycopg2

from app.config import DATABASE_URL

# Default connection factory (overridden in tests)
_connection_factory = None


def get_connection_factory():
    return _connection_factory or _default_connection_factory


def _default_connection_factory():
    """Create a PostgreSQL connection."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def set_connection_factory(factory):
    """Override the connection factory (used in tests)."""
    global _connection_factory
    _connection_factory = factory


def get_db():
    """Yield a database connection, closing it when done."""
    conn = get_connection_factory()()
    try:
        yield conn
    finally:
        conn.close()


def create_tables(conn):
    """Create the effect_entries table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS effect_entries (
            id SERIAL PRIMARY KEY,
            raw_id VARCHAR(13) NOT NULL,
            user_id VARCHAR(7) NOT NULL,
            pokemon_ability_id VARCHAR(10) NOT NULL,
            effect TEXT NOT NULL,
            language VARCHAR(50) NOT NULL,
            short_effect TEXT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
