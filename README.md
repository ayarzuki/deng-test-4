# Pokemon Ability API

A FastAPI application that processes Pokemon ability data by fetching from [PokeAPI](https://pokeapi.co/), normalizing `effect_entries`, storing them in PostgreSQL, and returning a structured JSON response.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
  - [Option 1: Docker Compose (Recommended)](#option-1-docker-compose-recommended)
  - [Option 2: Local Development with Virtual Environment](#option-2-local-development-with-virtual-environment)
- [API Usage](#api-usage)
- [Database Schema](#database-schema)
- [Data Architecture](#data-architecture)

---

## Prerequisites

- **Python 3.9+** (3.10 recommended)
- **Docker & Docker Compose** (for containerized setup)
- **PostgreSQL 15** (if running locally without Docker)

---

## Project Structure

```
flip/
├── app/
│   ├── __init__.py          # Package initializer
│   ├── config.py            # Environment variable configuration
│   ├── database.py          # SQLAlchemy engine, session, and Base
│   ├── main.py              # FastAPI app, endpoints, and business logic
│   ├── models.py            # SQLAlchemy ORM model (effect_entries table)
│   ├── schemas.py           # Pydantic request/response schemas
│   └── utils.py             # Helper functions (ID generation)
├── .env                     # Environment variables (DATABASE_URL)
├── .gitignore               # Git ignore rules
├── docker-compose.yml       # Docker Compose for API + PostgreSQL
├── Dockerfile               # Container image for FastAPI app
├── NEW_INSTRUCTION.md       # Original task instructions
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## How to Run

### Option 1: Docker Compose (Recommended)

This spins up both the FastAPI app and PostgreSQL in containers.

```bash
# Build and start all services
docker-compose up --build

# The API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

To stop:

```bash
docker-compose down
```

To stop and remove database volume:

```bash
docker-compose down -v
```

### Option 2: Local Development with Virtual Environment

**1. Create and activate virtual environment:**

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Set up PostgreSQL:**

Make sure PostgreSQL is running locally. Create the database:

```sql
CREATE DATABASE pokemon_db;
```

**4. Configure environment:**

Edit `.env` to point to your local database:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pokemon_db
```

**5. Run the application:**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive Swagger docs at `http://localhost:8000/docs`.

---

## API Usage

### POST `/pokemon-ability`

Process a Pokemon ability and store effect entries in the database.

**Request Body:**

```json
{
  "raw_id": "7dsa8d7sa9dsa",
  "user_id": "5199434",
  "pokemon_ability_id": "150"
}
```

> `raw_id` and `user_id` are optional. If omitted, they are auto-generated (13-char alphanumeric for `raw_id`, 7-digit integer for `user_id`).

**Response:**

```json
{
  "raw_id": "7dsa8d7sa9dsa",
  "user_id": "5199434",
  "returned_entries": [
    {
      "effect": "This Pokémon transforms into a random opponent upon entering battle...",
      "language": {
        "name": "en",
        "url": "https://pokeapi.co/api/v2/language/9/"
      },
      "short_effect": "Transforms upon entering battle."
    }
  ],
  "pokemon_list": ["ditto"]
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:8000/pokemon-ability \
  -H "Content-Type: application/json" \
  -d '{"pokemon_ability_id": "150"}'
```

### GET `/health`

Health check endpoint. Returns `{"status": "healthy"}`.

---

## Database Schema

### Table: `effect_entries`

| Column               | Type         | Description                                      |
|----------------------|--------------|--------------------------------------------------|
| `id`                 | INTEGER (PK) | Auto-incrementing primary key                    |
| `raw_id`             | VARCHAR(13)  | Request identifier (provided or auto-generated)  |
| `user_id`            | VARCHAR(7)   | User identifier (provided or auto-generated)     |
| `pokemon_ability_id` | VARCHAR(10)  | Pokemon ability ID from the request              |
| `effect`             | TEXT         | Full effect description from PokeAPI             |
| `language`           | VARCHAR(50)  | Language code (e.g., `en`, `de`)                 |
| `short_effect`       | TEXT         | Short effect description from PokeAPI            |

---

## Data Architecture

The diagram below illustrates the data flow from ingestion through to the Data Warehouse (DWH):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA ARCHITECTURE OVERVIEW                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐       ┌──────────────┐       ┌──────────────────────────┐
  │   Client /   │       │   FastAPI    │       │       PokeAPI            │
  │   Consumer   │──────▶│   Service    │──────▶│ /api/v2/ability/{id}    │
  │              │       │              │◀──────│                          │
  └──────────────┘       └──────┬───────┘       └──────────────────────────┘
                                │
                    Normalized effect_entries
                                │
                                ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                     1. STAGING ENVIRONMENT                             │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  stg_effect_entries (Raw Ingestion Table)                      │    │
  │  │                                                                │    │
  │  │  - id (PK)                                                     │    │
  │  │  - raw_id              ← request identifier                    │    │
  │  │  - user_id             ← user identifier                       │    │
  │  │  - pokemon_ability_id  ← ability ID                            │    │
  │  │  - effect              ← raw effect text                       │    │
  │  │  - language            ← language code                         │    │
  │  │  - short_effect        ← raw short effect text                 │    │
  │  │  - ingested_at         ← timestamp of ingestion                │    │
  │  │  - source              ← "pokeapi"                             │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  Purpose: Landing zone for raw data. No transformations applied.       │
  │  Data is appended as-is from each API call.                            │
  └────────────────────────────────┬───────────────────────────────────────┘
                                   │
                        Cleanse, deduplicate,
                        validate & conform
                                   │
                                   ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                 2. OPERATIONAL DATA STORE (ODS)                        │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  ods_abilities                                                 │    │
  │  │  - ability_id (PK)     ← pokemon_ability_id (deduplicated)     │    │
  │  │  - ability_name        ← resolved from PokeAPI                 │    │
  │  │  - updated_at                                                  │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  ods_effect_entries                                            │    │
  │  │  - id (PK)                                                     │    │
  │  │  - ability_id (FK)     ← references ods_abilities              │    │
  │  │  - language_code       ← standardized (ISO 639-1)              │    │
  │  │  - effect_text         ← cleaned effect                        │    │
  │  │  - short_effect_text   ← cleaned short effect                  │    │
  │  │  - updated_at                                                  │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  ods_request_log                                               │    │
  │  │  - id (PK)                                                     │    │
  │  │  - raw_id              ← original request ID                   │    │
  │  │  - user_id             ← requesting user                       │    │
  │  │  - ability_id (FK)                                             │    │
  │  │  - requested_at                                                │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  Purpose: Current-state, deduplicated, relationally normalized data.   │
  │  Supports operational queries and application reads.                   │
  └────────────────────────────────┬───────────────────────────────────────┘
                                   │
                        Aggregate, model into
                        star schema for analytics
                                   │
                                   ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                    3. DATA WAREHOUSE (DWH)                             │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  dim_ability  (Dimension)                                      │    │
  │  │  - ability_key (PK, surrogate)                                 │    │
  │  │  - ability_id (natural key)                                    │    │
  │  │  - ability_name                                                │    │
  │  │  - total_pokemon_count                                         │    │
  │  │  - available_languages                                         │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  dim_language  (Dimension)                                     │    │
  │  │  - language_key (PK, surrogate)                                │    │
  │  │  - language_code                                               │    │
  │  │  - language_name                                               │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  dim_user  (Dimension)                                         │    │
  │  │  - user_key (PK, surrogate)                                    │    │
  │  │  - user_id (natural key)                                       │    │
  │  │  - first_seen_at                                               │    │
  │  │  - total_requests                                              │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────────┐    │
  │  │  fact_ability_requests  (Fact)                                 │    │
  │  │  - request_key (PK, surrogate)                                 │    │
  │  │  - ability_key (FK → dim_ability)                              │    │
  │  │  - user_key (FK → dim_user)                                    │    │
  │  │  - language_key (FK → dim_language)                            │    │
  │  │  - raw_id                                                      │    │
  │  │  - effect_text                                                 │    │
  │  │  - short_effect_text                                           │    │
  │  │  - requested_at                                                │    │
  │  └────────────────────────────────────────────────────────────────┘    │
  │                                                                        │
  │  Purpose: Star schema optimized for analytical queries.                │
  │  Supports reporting on ability usage, language distribution,           │
  │  and user activity patterns.                                           │
  └────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────────┐
  │                         DATA FLOW SUMMARY                              │
  │                                                                        │
  │  Client Request                                                        │
  │       │                                                                │
  │       ▼                                                                │
  │  FastAPI ──▶ PokeAPI (fetch ability data)                             │
  │       │                                                                │
  │       ▼                                                                │
  │  Normalize effect_entries                                              │
  │       │                                                                │
  │       ├──▶ Staging (raw append, no transforms)                        │
  │       │         │                                                      │
  │       │         ▼                                                      │
  │       │    ODS (cleanse, deduplicate, normalize relations)             │
  │       │         │                                                      │
  │       │         ▼                                                      │
  │       │    DWH (aggregate into star schema for analytics)              │
  │       │                                                                │
  │       └──▶ JSON Response to Client                                    │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## License

This project is for technical assessment purposes.
