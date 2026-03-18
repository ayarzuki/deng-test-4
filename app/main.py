import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import EffectEntry
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
    Base.metadata.create_all(bind=engine)


@app.post("/pokemon-ability", response_model=PokemonAbilityResponse)
async def process_pokemon_ability(
    request: PokemonAbilityRequest,
    db: Session = Depends(get_db),
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
        db_entry = EffectEntry(
            raw_id=raw_id,
            user_id=user_id,
            pokemon_ability_id=ability_id,
            effect=entry["effect"],
            language=entry["language"]["name"],
            short_effect=entry["short_effect"],
        )
        db.add(db_entry)

    db.commit()

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
