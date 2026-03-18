import pytest
from pydantic import ValidationError

from app.schemas import PokemonAbilityRequest, PokemonAbilityResponse, ReturnedEntry


class TestPokemonAbilityRequest:
    def test_valid_full_request(self):
        req = PokemonAbilityRequest(
            raw_id="abc1234567890",
            user_id="1234567",
            pokemon_ability_id="150",
        )
        assert req.raw_id == "abc1234567890"
        assert req.user_id == "1234567"
        assert req.pokemon_ability_id == "150"

    def test_optional_fields_default_none(self):
        req = PokemonAbilityRequest(pokemon_ability_id="1")
        assert req.raw_id is None
        assert req.user_id is None

    def test_missing_pokemon_ability_id_raises(self):
        with pytest.raises(ValidationError):
            PokemonAbilityRequest()


class TestReturnedEntry:
    def test_valid_entry(self):
        entry = ReturnedEntry(
            effect="Some effect",
            language={"name": "en", "url": "https://pokeapi.co/api/v2/language/9/"},
            short_effect="Short effect",
        )
        assert entry.effect == "Some effect"
        assert entry.language["name"] == "en"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            ReturnedEntry(effect="test", language={"name": "en"})


class TestPokemonAbilityResponse:
    def test_valid_response(self):
        resp = PokemonAbilityResponse(
            raw_id="abc1234567890",
            user_id="1234567",
            returned_entries=[
                ReturnedEntry(
                    effect="Effect text",
                    language={"name": "en", "url": "https://example.com"},
                    short_effect="Short",
                )
            ],
            pokemon_list=["pikachu", "ditto"],
        )
        assert len(resp.returned_entries) == 1
        assert resp.pokemon_list == ["pikachu", "ditto"]

    def test_empty_lists(self):
        resp = PokemonAbilityResponse(
            raw_id="abc1234567890",
            user_id="1234567",
            returned_entries=[],
            pokemon_list=[],
        )
        assert resp.returned_entries == []
        assert resp.pokemon_list == []
