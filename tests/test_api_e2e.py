"""End-to-end tests that hit the real PokeAPI and verify the full flow."""

from app.models import EffectEntry


class TestPokemonAbilityEndpointE2E:
    """E2E tests against the real PokeAPI (requires internet)."""

    def test_full_flow_with_provided_ids(self, client, db_session):
        """Test: send request with raw_id & user_id, verify response + DB storage."""
        payload = {
            "raw_id": "7dsa8d7sa9dsa",
            "user_id": "5199434",
            "pokemon_ability_id": "150",
        }

        response = client.post("/pokemon-ability", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["raw_id"] == "7dsa8d7sa9dsa"
        assert data["user_id"] == "5199434"
        assert isinstance(data["returned_entries"], list)
        assert isinstance(data["pokemon_list"], list)

        # Verify returned_entries have correct structure
        for entry in data["returned_entries"]:
            assert "effect" in entry
            assert "language" in entry
            assert "short_effect" in entry
            assert "name" in entry["language"]
            assert "url" in entry["language"]

        # Verify pokemon_list contains pokemon names (strings)
        for name in data["pokemon_list"]:
            assert isinstance(name, str)
            assert len(name) > 0

        # Verify data was stored in database
        db_entries = db_session.query(EffectEntry).all()
        assert len(db_entries) == len(data["returned_entries"])

        for db_entry in db_entries:
            assert db_entry.raw_id == "7dsa8d7sa9dsa"
            assert db_entry.user_id == "5199434"
            assert db_entry.pokemon_ability_id == "150"
            assert db_entry.effect is not None
            assert db_entry.language is not None
            assert db_entry.short_effect is not None

    def test_full_flow_auto_generated_ids(self, client, db_session):
        """Test: send request without raw_id & user_id, verify they are generated."""
        payload = {"pokemon_ability_id": "1"}

        response = client.post("/pokemon-ability", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify auto-generated IDs
        assert len(data["raw_id"]) == 13
        assert len(data["user_id"]) == 7
        assert data["user_id"].isdigit()

        # Verify returned_entries exist
        assert len(data["returned_entries"]) > 0

        # Verify pokemon_list exists
        assert len(data["pokemon_list"]) > 0

        # Verify DB storage
        db_entries = db_session.query(EffectEntry).all()
        assert len(db_entries) == len(data["returned_entries"])

    def test_ability_with_known_data(self, client, db_session):
        """Test ability ID 1 (stench) - a well-known ability with stable data."""
        payload = {
            "raw_id": "testknown1234",
            "user_id": "9999999",
            "pokemon_ability_id": "1",
        }

        response = client.post("/pokemon-ability", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Ability 1 is "stench" - should have effect_entries
        assert len(data["returned_entries"]) > 0

        # Should have English entry
        languages = [e["language"]["name"] for e in data["returned_entries"]]
        assert "en" in languages

        # Should have pokemon in list
        assert len(data["pokemon_list"]) > 0

    def test_invalid_ability_id_returns_error(self, client):
        """Test: invalid ability ID should return error from PokeAPI."""
        payload = {"pokemon_ability_id": "999999"}

        response = client.post("/pokemon-ability", json=payload)

        assert response.status_code == 404

    def test_missing_pokemon_ability_id_returns_422(self, client):
        """Test: missing required field returns validation error."""
        payload = {"raw_id": "abc1234567890", "user_id": "1234567"}

        response = client.post("/pokemon-ability", json=payload)

        assert response.status_code == 422

    def test_multiple_requests_accumulate_in_db(self, client, db_session):
        """Test: multiple requests should all be stored independently."""
        for ability_id in ["1", "2"]:
            payload = {"pokemon_ability_id": ability_id}
            response = client.post("/pokemon-ability", json=payload)
            assert response.status_code == 200

        # Verify both requests stored entries
        entries_ability_1 = (
            db_session.query(EffectEntry)
            .filter(EffectEntry.pokemon_ability_id == "1")
            .all()
        )
        entries_ability_2 = (
            db_session.query(EffectEntry)
            .filter(EffectEntry.pokemon_ability_id == "2")
            .all()
        )

        assert len(entries_ability_1) > 0
        assert len(entries_ability_2) > 0
