"""
Raw SQL helpers for the effect_entries table.

No ORM — all queries use plain SQL via DB-API connections (psycopg2).
"""

TABLE_NAME = "effect_entries"


def insert_effect_entry(cursor, raw_id, user_id, pokemon_ability_id, effect, language, short_effect):
    """Insert a single effect entry row."""
    cursor.execute(
        f"""
        INSERT INTO {TABLE_NAME} (raw_id, user_id, pokemon_ability_id, effect, language, short_effect)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (raw_id, user_id, pokemon_ability_id, effect, language, short_effect),
    )


def query_all_effect_entries(cursor):
    """Return all rows from effect_entries as a list of dicts."""
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def query_effect_entries_by_ability(cursor, pokemon_ability_id):
    """Return rows filtered by pokemon_ability_id."""
    cursor.execute(
        f"SELECT * FROM {TABLE_NAME} WHERE pokemon_ability_id = %s",
        (pokemon_ability_id,),
    )
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
