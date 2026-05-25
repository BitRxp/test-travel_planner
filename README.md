# Travel Planner API

A RESTful API for managing travel projects and places. Built with FastAPI, SQLite, and the Art Institute of Chicago API.

---

## Features

- Create and manage travel projects with optional places, description, and start date
- Add places to projects — each place is validated against the [Art Institute of Chicago API](https://api.artic.edu/docs/)
- Add and update notes on places
- Mark places as visited — when all places are visited, the project is automatically marked as completed
- A project cannot be deleted if any of its places have been visited
- Maximum 10 places per project, no duplicates allowed
- Pagination and filtering on listing endpoints
- TTL caching for Art Institute API responses
- HTTP Basic Authentication
- Interactive API docs via Swagger UI

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | SQLite via SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| HTTP Client | httpx (async) |
| Caching | cachetools TTLCache |
| Auth | HTTP Basic Auth |

---

## Project Structure

```
app/
├── main.py              # App factory, router registration
├── config.py            # Settings via pydantic-settings
├── database.py          # SQLAlchemy engine, session, Base
├── models/
│   ├── project.py       # TravelProject model
│   └── place.py         # ProjectPlace model
├── schemas/
│   ├── project.py       # ProjectCreate, ProjectUpdate, ProjectResponse
│   └── place.py         # PlaceCreate, PlaceUpdate, PlaceResponse
├── crud/
│   ├── projects.py      # DB queries for projects
│   └── places.py        # DB queries for places
├── services/
│   ├── projects.py      # Business logic for projects
│   └── places.py        # Business logic for places
├── routers/
│   ├── projects.py      # /projects endpoints
│   └── places.py        # /projects/{id}/places endpoints
├── core/
│   ├── dependencies.py  # get_db, get_current_user
│   ├── exceptions.py    # Custom exceptions + handlers
│   └── security.py      # Password verification
└── artic/
    ├── client.py        # Art Institute API client
    ├── schemas.py       # API response schemas
    └── cache.py         # TTL cache wrapper
```

---

## Setup

### Local (without Docker)

**1. Clone the repository**
```bash
git clone https://github.com/BitRxp/test-travel-planner.git
cd test-travel-planner
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` if needed (defaults work out of the box):
```env
DATABASE_URL=sqlite:///./travel_planner.db
AUTH_USERNAME=admin
AUTH_PASSWORD=secret
ARTIC_BASE_URL=https://api.artic.edu/api/v1
ARTIC_CACHE_TTL=300
ARTIC_CACHE_MAX_SIZE=512
API_PREFIX=/api/v1
```

**5. Run database migrations**
```bash
alembic upgrade head
```

**6. Start the server**
```bash
uvicorn app.main:app --reload
```

API is available at: `http://localhost:8000`

---

### Docker

```bash
cp .env.example .env
docker-compose up --build
```

API is available at: `http://localhost:8000`

---

## API Documentation

Interactive Swagger UI: `http://localhost:8000/docs`

Click **Authorize** and enter credentials (`admin` / `secret`) to authenticate all requests.

Postman Collection: import `travel_planner.postman_collection.json` from the repository root.

---

## Authentication

All API endpoints require **HTTP Basic Auth**.

| Field | Default value |
|-------|--------------|
| Username | `admin` |
| Password | `secret` |

---

## Endpoints

### Projects

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/projects` | Create a project (optionally with places) |
| `GET` | `/api/v1/projects` | List all projects |
| `GET` | `/api/v1/projects/{id}` | Get a single project |
| `PUT` | `/api/v1/projects/{id}` | Update project info |
| `DELETE` | `/api/v1/projects/{id}` | Delete a project |

**Query parameters for listing:**

| Param | Type | Description |
|-------|------|-------------|
| `skip` | int | Offset (default: 0) |
| `limit` | int | Page size (default: 20) |
| `status` | string | Filter by `active` or `completed` |

### Places

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/projects/{id}/places` | Add a place to a project |
| `GET` | `/api/v1/projects/{id}/places` | List places in a project |
| `GET` | `/api/v1/projects/{id}/places/{place_id}` | Get a single place |
| `PATCH` | `/api/v1/projects/{id}/places/{place_id}` | Update notes or visited status |

**Query parameters for listing:**

| Param | Type | Description |
|-------|------|-------------|
| `skip` | int | Offset (default: 0) |
| `limit` | int | Page size (default: 20) |
| `visited` | bool | Filter by `true` or `false` |

---

## Example Requests

### Create a project with places

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -u admin:secret \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Art Trip",
    "description": "Visiting top museums",
    "start_date": "2026-06-01T00:00:00",
    "places": [
      { "external_id": 16568 },
      { "external_id": 16571 }
    ]
  }'
```

**Response `201`:**
```json
{
  "id": 1,
  "name": "My Art Trip",
  "description": "Visiting top museums",
  "start_date": "2026-06-01T00:00:00",
  "status": "active",
  "created_at": "2026-05-25T10:00:00",
  "places": [
    {
      "id": 1,
      "project_id": 1,
      "external_id": 16568,
      "title": "Water Lilies",
      "image_url": "https://www.artic.edu/iiif/2/3c27b499-af56-f0d5-93b5-a7f2f1ad5813/full/843,/0/default.jpg",
      "notes": null,
      "visited": false,
      "created_at": "2026-05-25T10:00:00"
    }
  ]
}
```

---

### Add a place to an existing project

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/places \
  -u admin:secret \
  -H "Content-Type: application/json" \
  -d '{ "external_id": 27992 }'
```

**Response `201`:**
```json
{
  "id": 3,
  "project_id": 1,
  "external_id": 27992,
  "title": "A Sunday on La Grande Jatte — 1884",
  "image_url": "https://www.artic.edu/iiif/2/2d484387-2509-5e8e-2c43-22f9981972eb/full/843,/0/default.jpg",
  "notes": null,
  "visited": false,
  "created_at": "2026-05-25T10:05:00"
}
```

---

### Update notes and mark as visited

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/places/1 \
  -u admin:secret \
  -H "Content-Type: application/json" \
  -d '{ "notes": "Stunning impressionist collection", "visited": true }'
```

**Response `200`:**
```json
{
  "id": 1,
  "project_id": 1,
  "external_id": 16568,
  "title": "Water Lilies",
  "image_url": "https://www.artic.edu/iiif/2/3c27b499-af56-f0d5-93b5-a7f2f1ad5813/full/843,/0/default.jpg",
  "notes": "Stunning impressionist collection",
  "visited": true,
  "created_at": "2026-05-25T10:00:00"
}
```

---

### List projects filtered by status

```bash
curl "http://localhost:8000/api/v1/projects?status=active" -u admin:secret
```

---

### List places filtered by visited

```bash
curl "http://localhost:8000/api/v1/projects/1/places?visited=false" -u admin:secret
```

---

## Business Rules

| Rule | Behaviour |
|------|-----------|
| Max places per project | 10 — returns `422` if exceeded |
| Duplicate places | Not allowed in the same project — returns `409` |
| Delete with visited places | Not allowed — returns `409` |
| Place validation | Checked against Art Institute API before saving — returns `404` if not found |
| Auto-complete project | When all places are marked visited, project status becomes `completed` automatically |

---

## Error Responses

All errors follow the format:

```json
{ "detail": "Error message here" }
```

| Status | Meaning |
|--------|---------|
| `401` | Missing or invalid credentials |
| `404` | Project or place not found / artwork not found in Art Institute API |
| `409` | Duplicate place / project has visited places |
| `422` | Validation error (e.g. place limit exceeded, invalid input) |
| `502` | Art Institute API unavailable |

---

## Design Decisions

- **Layer separation** — routers, services, crud, and schemas are split into dedicated folders rather than grouped by feature. Each layer has a single responsibility and only knows about the layer below it: `routers/` → `services/` → `crud/`.

- **No JWT** — HTTP Basic Auth is sufficient for this scope. JWT would add complexity (token issuance, refresh logic, expiry handling) without benefit since there are no user accounts stored in the database.

- **Artwork validation order** — when adding a place, limit and duplicate checks run before the Art Institute API call. Cheap DB checks are always preferred over network requests.

- **TTL cache for Art Institute API** — artwork metadata rarely changes, so responses are cached in-memory for 5 minutes. This reduces latency and avoids unnecessary external requests on repeated lookups.

- **Auto-complete via service layer** — when a place is marked as visited, the project status is recalculated automatically. The trigger lives in the service layer, not in the model or router, keeping each layer free of concerns it shouldn't own.

---

## Author

Developed by **Oleksandr Taranenko**
GitHub: [github.com/BitRxp](https://github.com/BitRxp)
