from app.models import insert_effect_entry, query_all_effect_entries, TABLE_NAME


class TestEffectEntryModel:
    def test_create_and_query(self, db_connection):
        cursor = db_connection.cursor()
        insert_effect_entry(
            cursor,
            raw_id="abc1234567890",
            user_id="1234567",
            pokemon_ability_id="150",
            effect="Test effect description",
            language="en",
            short_effect="Test short effect",
        )
        db_connection.commit()

        rows = query_all_effect_entries(cursor)
        cursor.close()

        assert len(rows) == 1
        row = rows[0]
        assert row["raw_id"] == "abc1234567890"
        assert row["user_id"] == "1234567"
        assert row["pokemon_ability_id"] == "150"
        assert row["effect"] == "Test effect description"
        assert row["language"] == "en"
        assert row["short_effect"] == "Test short effect"
        assert row["id"] is not None

    def test_multiple_entries(self, db_connection):
        cursor = db_connection.cursor()
        for i in range(3):
            insert_effect_entry(
                cursor,
                raw_id="abc1234567890",
                user_id="1234567",
                pokemon_ability_id="150",
                effect=f"Effect {i}",
                language="en",
                short_effect=f"Short {i}",
            )
        db_connection.commit()

        rows = query_all_effect_entries(cursor)
        cursor.close()

        assert len(rows) == 3

    def test_table_name(self):
        assert TABLE_NAME == "effect_entries"
