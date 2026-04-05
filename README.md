# Zorvyn Finance API

A **Finance Data Processing and Access Control Backend** built with FastAPI, SQLAlchemy, SQLite, and JWT authentication.

## Tech Stack

| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance async web framework with auto-generated OpenAPI docs |
| **SQLAlchemy** | ORM for database models and DB-level aggregation queries |
| **SQLite** | Zero-config local database (swap to PostgreSQL in prod via `DATABASE_URL`) |
| **JWT (python-jose)** | Stateless authentication — no session storage, scales horizontally |
| **bcrypt** | Industry-standard password hashing |
| **Pydantic v2** | Request/response validation with type safety |

## Setup

```bash
# Clone and navigate
cd finance-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

**Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Default Admin

A default admin user is seeded on startup:

| Field | Value |
|---|---|
| Email | `admin@zorvyn.com` |
| Password | `admin123` |
| Role | `admin` |

## Role Model

| Permission | Admin | Analyst | Viewer |
|---|:---:|:---:|:---:|
| Register / Login | ✅ | ✅ | ✅ |
| View records | ✅ | ✅ | ✅ |
| View dashboard | ✅ | ✅ | ✅ |
| Create records | ✅ | ✅ | ❌ |
| Update records | ✅ | ✅ | ❌ |
| Delete records (soft) | ✅ | ❌ | ❌ |
| Manage users | ✅ | ❌ | ❌ |

## API Endpoints

### Authentication (Public)

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and get JWT token |

### Current User (All Roles)

| Method | Path | Description |
|---|---|---|
| `GET` | `/users/me` | Get currently authenticated user's profile |

### Users (Admin Only)

| Method | Path | Description |
|---|---|---|
| `GET` | `/users/` | List all users |
| `PATCH` | `/users/{id}/role` | Update user role |
| `PATCH` | `/users/{id}/status` | Toggle active status |

### Financial Records

| Method | Path | Roles | Description |
|---|---|---|---|
| `POST` | `/records/` | Admin, Analyst | Create record |
| `GET` | `/records/` | All | List (paginated, filterable) |
| `GET` | `/records/{id}` | All | Get single record |
| `PATCH` | `/records/{id}` | Admin, Analyst | Partial update |
| `DELETE` | `/records/{id}` | Admin | Soft delete |

**Query Params**: `type`, `category`, `date_from`, `date_to`, `page`, `limit`

### Dashboard

| Method | Path | Roles | Description |
|---|---|---|---|
| `GET` | `/dashboard/summary` | All | Income, expenses, net balance, count |
| `GET` | `/dashboard/categories` | All | Category-wise totals |
| `GET` | `/dashboard/trends` | All | Weekly/monthly trends (last 6 periods) |

## Design Decisions

- **Soft Delete**: Financial records are never permanently destroyed — `is_deleted` flag preserves audit trail integrity
- **DB-Level Aggregations**: Dashboard computations use `func.sum`, `func.count`, `GROUP BY` at the SQL level for performance (not Python loops)
- **JWT Stateless Auth**: No server-side session storage needed, scales cleanly across instances
- **SQLite**: Zero-infrastructure local development; swap to PostgreSQL by changing the database URL
- **HTTPBearer Security**: All protected endpoints show lock icons in Swagger UI
- **CORS**: `allow_origins=["*"]` is intentionally set for local development only and must be restricted to specific trusted origins in production

## Assumptions

- Single-tenant application (no org/team scoping)
- SQLite is sufficient for development; production would use PostgreSQL
- Token expiry is 60 minutes; no refresh token mechanism
- All financial amounts are stored as `Numeric(12,2)` — no floating point precision loss
- Password minimum length is 8 characters
- Admins cannot modify their own role or status
- Trends endpoint now accepts a `limit` param (1–24, default 6)
- Added `GET /users/me` to the API table under Users section, with "All roles" access
- Soft-deleted records are excluded from all queries and dashboard aggregations

## Deployment

### Render (recommended)

The repo includes a `render.yaml` blueprint — connect your GitHub repo on [Render](https://render.com) and it deploys automatically.

### Docker

```bash
docker build -t zorvyn-finance .
docker run -p 8000:8000 zorvyn-finance
```

## Quick Test

```bash
BASE=http://localhost:8000

# Login as admin
TOKEN=$(curl -s -X POST $BASE/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@zorvyn.com","password":"admin123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Create a record
curl -s -X POST $BASE/records/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"amount":5000,"type":"income","category":"Salary","date":"2026-04-01"}'

# View dashboard
curl -s $BASE/dashboard/summary -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```
