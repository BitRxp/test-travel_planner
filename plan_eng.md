# Travel Planner — Plan

---

## Project Structure

```
travel_planner/
│
├── app/
│   ├── main.py                         # FastAPI app factory, router registration
│   ├── config.py                       # Settings via pydantic-settings (.env)
│   ├── database.py                     # SQLAlchemy engine, SessionLocal, Base
│   │
│   ├── models/                         # SQLAlchemy models — one file per model
│   │   ├── __init__.py                 # Import all models (required by Alembic)
│   │   ├── project.py                  # TravelProject
│   │   └── place.py                    # ProjectPlace
│   │
│   ├── schemas/                        # Pydantic schemas — one file per model
│   │   ├── __init__.py
│   │   ├── project.py                  # ProjectCreate, ProjectUpdate, ProjectResponse
│   │   └── place.py                    # PlaceCreate, PlaceUpdate, PlaceResponse
│   │
│   ├── crud/                           # DB operations only — one file per domain
│   │   ├── __init__.py
│   │   ├── projects.py                 # create, get, get_list, update, delete
│   │   └── places.py                   # create, get, get_list, update, count_by_project, check_duplicate
│   │
│   ├── services/                       # Business logic — one file per domain
│   │   ├── __init__.py
│   │   ├── projects.py                 # completed status, delete guard
│   │   └── places.py                   # limit 10, duplicate check, auto-complete project
│   │
│   ├── routers/                        # FastAPI routers — one file per domain
│   │   ├── __init__.py
│   │   ├── projects.py                 # /projects, /projects/{id}
│   │   └── places.py                   # /projects/{id}/places, /projects/{id}/places/{place_id}
│   │
│   ├── core/                           # Shared utilities
│   │   ├── dependencies.py             # get_db, get_current_user (Depends)
│   │   ├── exceptions.py               # Custom exceptions + handlers
│   │   └── security.py                 # HTTP Basic auth
│   │
│   └── artic/                          # Art Institute of Chicago API integration
│       ├── client.py                   # httpx AsyncClient: get_artwork, search_artworks
│       ├── schemas.py                  # Pydantic schemas for external API responses
│       └── cache.py                    # TTL cache (cachetools.TTLCache)
│
├── migrations/                         # Alembic
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── conftest.py                     # Fixtures: test DB, client, mocks
│   ├── test_projects.py
│   ├── test_places.py
│   └── test_artic.py
│
├── .env
├── .env.example
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

### Layer Separation Principles

| Layer | Folder | Responsible for |
|-------|--------|-----------------|
| **Routers** | `routers/` | HTTP: receive request, return response, status codes |
| **Services** | `services/` | Business logic: rules, orchestration, external service calls |
| **CRUD** | `crud/` | DB queries only — no logic whatsoever |
| **Schemas** | `schemas/` | Input/output validation via Pydantic |
| **Models** | `models/` | SQLAlchemy table definitions |

`routers/` → `services/` → `crud/` (each layer only knows about the one below it, never the reverse)

Each file inside a folder = one domain (`projects.py`, `places.py`)

---

### Dependencies (requirements.txt)

```
fastapi
uvicorn[standard]
sqlalchemy
alembic
pydantic-settings
httpx
cachetools
passlib[bcrypt]        # for Basic Auth
python-dotenv
pytest
pytest-asyncio
httpx                  # FastAPI test client
```

---

## Implementation Steps

---

### Step 1 — Initialization

- Create all folders according to the structure above
- Set up virtual environment, `requirements.txt`
- `app/config.py` — settings via `pydantic-settings` + `.env`
- `app/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`
- `app/main.py` — create FastAPI app, register routers and exception handlers
- Set up Alembic (`alembic init migrations`, configure `env.py`)

---

### Step 2 — Models (`app/models/`)

- `models/project.py` — `TravelProject`: `id`, `name`, `description`, `start_date`, `status` (active/completed), `created_at`
- `models/place.py` — `ProjectPlace`: `id`, `project_id` (FK), `external_id`, `title`, `image_url`, `notes`, `visited`, `created_at`
- `models/__init__.py` — import both models (required for Alembic autogenerate)
- Create and apply the first migration

---

### Step 3 — Schemas (`app/schemas/`)

- `schemas/project.py` — `ProjectCreate`, `ProjectUpdate`, `ProjectResponse` (with nested places list)
- `schemas/place.py` — `PlaceCreate`, `PlaceUpdate`, `PlaceResponse`

---

### Step 4 — Art Institute API Integration (`app/artic/`)

- `artic/schemas.py` — Pydantic schema for API response (`ArtworkResponse`)
- `artic/cache.py` — `TTLCache` wrapper (cachetools)
- `artic/client.py` — `httpx.AsyncClient`: `get_artwork(id)`, `search_artworks(q)`
  - `GET https://api.artic.edu/api/v1/artworks/{id}`
  - `GET https://api.artic.edu/api/v1/artworks/search`

---

### Step 5 — CRUD (`app/crud/`)

- `crud/projects.py` — `create`, `get_by_id`, `get_list`, `update`, `delete`
- `crud/places.py` — `create`, `get_by_id`, `get_list`, `update`, `count_by_project`, `check_duplicate`

Rule: no business logic — only clean SQLAlchemy DB queries.

---

### Step 6 — Services (`app/services/`)

- `services/projects.py`:
  - Create project (+ validate and attach places from request)
  - Update project
  - Delete project (blocked if any place is `visited`)
  - Check and update project status → `completed`
- `services/places.py`:
  - Add place: validate via `artic/client`, check limit (≤10), check duplicate
  - Update place (`notes`, `visited`)
  - After `visited` update — trigger project status check

---

### Step 7 — Routers (`app/routers/`)

- `routers/projects.py`:

| Method | Path | Service |
|--------|------|---------|
| `POST` | `/projects` | `services/projects.create_project` |
| `GET` | `/projects` | `services/projects.get_projects` |
| `GET` | `/projects/{id}` | `services/projects.get_project` |
| `PUT` | `/projects/{id}` | `services/projects.update_project` |
| `DELETE` | `/projects/{id}` | `services/projects.delete_project` |

- `routers/places.py`:

| Method | Path | Service |
|--------|------|---------|
| `POST` | `/projects/{id}/places` | `services/places.add_place` |
| `GET` | `/projects/{id}/places` | `services/places.get_places` |
| `GET` | `/projects/{id}/places/{place_id}` | `services/places.get_place` |
| `PATCH` | `/projects/{id}/places/{place_id}` | `services/places.update_place` |

---

### Step 8 — Core (`app/core/`)

- `core/exceptions.py` — `ProjectNotFound`, `PlaceNotFound`, `PlaceLimitExceeded`, `DuplicatePlace`, `ProjectHasVisitedPlaces` + register handlers in `main.py`
- `core/dependencies.py` — `get_db` (session generator), `get_current_user`
- `core/security.py` — HTTP Basic auth via `passlib`

---

### Step 9 — Bonus Features

- **Docker** — `Dockerfile` + `docker-compose.yml`
- **Pagination** — `skip`/`limit` query params on `GET /projects` and `GET /projects/{id}/places`
- **Caching** — wire `artic/cache.py` into `artic/client.py`
- **Authentication** — add `core/security.py` as `Depends` in routers

---

### Step 10 — Finalization

- `README.md` — setup, run instructions, environment variables, example requests
- Postman Collection — all endpoints with examples
- Review commit history for meaningful messages
- Publish on GitHub
