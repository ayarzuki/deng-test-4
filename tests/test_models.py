from app.models import EffectEntry


class TestEffectEntryModel:
    def test_create_and_query(self, db_session):
        entry = EffectEntry(
            raw_id="abc1234567890",
            user_id="1234567",
            pokemon_ability_id="150",
            effect="Test effect description",
            language="en",
            short_effect="Test short effect",
        )
        db_session.add(entry)
        db_session.commit()

        result = db_session.query(EffectEntry).first()
        assert result is not None
        assert result.raw_id == "abc1234567890"
        assert result.user_id == "1234567"
        assert result.pokemon_ability_id == "150"
        assert result.effect == "Test effect description"
        assert result.language == "en"
        assert result.short_effect == "Test short effect"
        assert result.id is not None

    def test_multiple_entries(self, db_session):
        entries = [
            EffectEntry(
                raw_id="abc1234567890",
                user_id="1234567",
                pokemon_ability_id="150",
                effect=f"Effect {i}",
                language="en",
                short_effect=f"Short {i}",
            )
            for i in range(3)
        ]
        db_session.add_all(entries)
        db_session.commit()

        results = db_session.query(EffectEntry).all()
        assert len(results) == 3

    def test_table_name(self):
        assert EffectEntry.__tablename__ == "effect_entries"
