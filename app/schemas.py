from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PokemonAbilityRequest(BaseModel):
    raw_id: Optional[str] = None
    user_id: Optional[str] = None
    pokemon_ability_id: str


class LanguageInfo(BaseModel):
    name: str
    url: str


class ReturnedEntry(BaseModel):
    effect: str
    language: Dict[str, Any]
    short_effect: str


class PokemonAbilityResponse(BaseModel):
    raw_id: str
    user_id: str
    returned_entries: List[ReturnedEntry]
    pokemon_list: List[str]
