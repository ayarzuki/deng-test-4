import httpx
from fastapi import Depends, FastAPI, HTTPException

from app.database import create_tables, get_db
from app.models import insert_effect_entry
from app.schemas import PokemonAbilityRequest, PokemonAbilityResponse, ReturnedEntry
from app.utils import generate_raw_id, generate_user_id

app = FastAPI(
    title="Pokemon Ability API",
    description="FastAPI app to process Pokemon ability data from PokeAPI",
    version="1.0.0",
)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/ability"


@app.on_event("startup")
def on_startup():
    from app.database import get_connection_factory

    conn = get_connection_factory()()
    try:
        create_tables(conn)
    finally:
        conn.close()


@app.post("/pokemon-ability", response_model=PokemonAbilityResponse)
async def process_pokemon_ability(
    request: PokemonAbilityRequest,
    conn=Depends(get_db),
):
    raw_id = request.raw_id or generate_raw_id()
    user_id = request.user_id or generate_user_id()
    ability_id = request.pokemon_ability_id

    # Fetch data from PokeAPI
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKEAPI_BASE_URL}/{ability_id}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch ability {ability_id} from PokeAPI",
        )

    api_data = response.json()

    # Normalize effect_entries
    returned_entries = []
    cursor = conn.cursor()
    for entry in api_data.get("effect_entries", []):
        normalized = ReturnedEntry(
            effect=entry["effect"],
            language={
                "name": entry["language"]["name"],
                "url": entry["language"]["url"],
            },
            short_effect=entry["short_effect"],
        )
        returned_entries.append(normalized)

        # Store in database
        insert_effect_entry(
            cursor,
            raw_id=raw_id,
            user_id=user_id,
            pokemon_ability_id=ability_id,
            effect=entry["effect"],
            language=entry["language"]["name"],
            short_effect=entry["short_effect"],
        )

    conn.commit()
    cursor.close()

    # Extract pokemon list
    pokemon_list = [
        p["pokemon"]["name"] for p in api_data.get("pokemon", [])
    ]

    return PokemonAbilityResponse(
        raw_id=raw_id,
        user_id=user_id,
        returned_entries=returned_entries,
        pokemon_list=pokemon_list,
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
