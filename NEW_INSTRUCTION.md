# Technical Test Instructions

## Objective
Create a FastAPI framework in Python (preferably version 3.9+) to process Pokemon ability data.

## Task 1: FastAPI Development
The application should perform the following steps:

1.  **Receive Input JSON:** Parse data from an incoming JSON request.
    *   *Example Input:*
        ```json
        {
          "raw_id": "7dsa8d7sa9dsa",
          "user_id": "5199434",
          "pokemon_ability_id": "150"
        }
        ```
    *   *Example Output:*
        ```json
        {
          "raw_id": "7dsa8d7sa9dsa",
          "user_id": "5199434",
          "returned_entries": [
            {"effect":"Pokémon mit dieser Fähigkeit kopieren einen zufälligen Gegner. Der Effekt ist identisch mit transform.","language":{"name":"de","url":"https://pokeapi.co/api/v2/language/6/"},"short_effect":"Verwandelt sich beim Betreten des Kampfes in den Gegner."},
            {"effect":"This Pokémon transforms into a random opponent upon entering battle. This effect is identical to the move transform.","language":{"name":"en","url":"https://pokeapi.co/api/v2/language/9/"},"short_effect":"Transforms upon entering battle."}
          ],
          "pokemon_list": ["ditto"]
        }
        ```
2.  **API Integration:** Hit the following endpoint: `https://pokeapi.co/api/v2/ability/{pokemon_ability_id}`
3.  **Data Normalization:** Extract and normalize the `effect_entries` dictionary from the API response.
4.  **Database Storage:** Store the normalized `effect_entries` in one of the following databases:
    *   PostgreSQL
    *   *Table Format:* `id`, `raw_id`, `user_id`, `pokemon_ability_id`, `effect`, `language`, `short_effect`.
5.  **Return JSON Response:** Return a JSON object containing:
    *   `raw_id`
    *   `user_id`
    *   `returned_entries` (the normalized data)
    *   `pokemon_list` (list of pokemon names that have this ability)
6.  **ID Generation:** If not provided, generate a random string + int (length 13) for `raw_id` and a random int (length 7) for `user_id`.
7.  **Containerization :** Provide a `Dockerfile` and `docker-compose.yml` to containerize the FastAPI app and the database.

---

## Task 2: Data Architecture
Create a data architecture diagram visualizing the ingestion of the dataset into:
1.  **Staging Environment**
2.  **Operational Data Store (ODS)**
3.  **Data Warehouse (DWH)**
