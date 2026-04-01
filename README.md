# Finance Data Processing and Access Control Backend

Backend service for a finance dashboard system with:
- User and role management
- Financial record CRUD + filtering
- Record search endpoint
- Soft delete for records
- Dashboard summary analytics
- Role-based access control (RBAC)
- Rate limiting middleware
- Centralized request and service logging
- Validation and structured error handling

## Tech Stack

- Python 3.13+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL (`asyncpg`)
- JWT authentication (`python-jose`)

## Project Structure

- `backend/main.py`: app entry, middleware, routes, FastAPI lifespan startup
- `backend/core/`: config, security, exception handlers
- `backend/db/`: SQLAlchemy base, engine, sessions
- `backend/models/`: user and financial record models
- `backend/schemas/`: request/response validation models
- `backend/services/`: business logic
- `backend/api/routes/`: route handlers
- `backend/api/rbac.py`: role checks
- `backend/api/dependencies.py`: current-user auth dependency

## Roles and Access Rules

Roles:
- `viewer`
- `analyst`
- `admin`

Permissions:
- Viewer:
	- Can access dashboard summary endpoint
	- Cannot create/update/delete records
	- Cannot list records
	- Cannot manage users
- Analyst:
	- Can list/filter records
	- Can access dashboard summary endpoint
	- Cannot create/update/delete records
	- Cannot manage users
- Admin:
	- Full access to user and record management
	- Can access all summaries (global or per-user)

## Authentication Flow

1. Bootstrap first admin (one-time): `POST /users/bootstrap-admin`
2. Login: `POST /auth/login` (form fields: `username` = email, `password`)
3. Use returned bearer token in `Authorization: Bearer <token>`

## API Endpoints

### Auth

- `POST /auth/login`

### Users

- `POST /users/bootstrap-admin` (public, one-time only)
- `POST /users/` (admin)
- `GET /users/` (admin)
- `PATCH /users/{user_id}` (admin)

### Financial Records

- `POST /records/` (admin)
- `GET /records/` (admin, analyst)
	- Supports query params:
		- `page`, `limit`
		- `category`
		- `record_type` (`income` or `expense`)
		- `start_date`, `end_date`
		- `user_id` (admin-only behavior)
- `PATCH /records/{record_id}` (admin)
- `DELETE /records/{record_id}` (admin)
	- Uses soft delete (`is_deleted=true`, `deleted_at` timestamp)
- `GET /records/search` (admin, analyst)
	- Query params: `q`, `page`, `limit`, optional `user_id`

### Dashboard Summary

- `GET /summary/` (viewer, analyst, admin)
	- Supports optional `user_id` (effective for admin)
	- Returns:
		- `total_income`
		- `total_expense`
		- `net_balance`
		- `category_totals`
		- `recent_activity` (last 5)
		- `monthly_trends`

## Data Model

### User

- `id`
- `name`
- `email` (unique)
- `hashed_password`
- `role` (`admin`, `analyst`, `viewer`)
- `is_active`
- `created_at`

### FinancialRecord

- `id`
- `user_id` (FK to user)
- `amount`
- `type` (`income`, `expense`)
- `category`
- `date`
- `note`
- `created_at`

## Validation and Error Handling

- Pydantic validation for request payloads
	- Positive amount validation (`amount > 0`)
	- Category length constraints
- Standard HTTP status codes
- Consistent JSON error response via exception handlers
- Invalid credentials return `401`
- Insufficient role returns `403`
- Missing resources return `404`
- Excess requests return `429`

## Logging

- Structured app logs for incoming requests with latency and status codes
- Service-level logs for user auth/updates and record create/update/delete

## Rate Limiting

- SlowAPI middleware is enabled globally.
- Default policy is configured in `backend/core/rate_limiter.py` as `100/minute`.
- You can tune limits in `.env` with `RATE_LIMIT_MAX_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` for app-level config needs.

## Setup

1. Create and activate virtual environment
2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment in `.env`

You can copy from `.env.example` and adjust values for local setup.

Required values:
- `APP_NAME`
- `ACCESS_TOKEN_SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL`

4. Run API

```bash
uvicorn backend.main:app --reload
```

Open docs:
- Swagger UI: `http://127.0.0.1:8000/docs`

## Tests

Run tests:

```bash
pytest -q
```

Current tests cover:
- soft delete behavior
- search endpoint behavior
- rate limiter behavior

## Assignment Requirement Mapping

1. User and Role Management
- User creation/update/listing and role assignment are implemented.
- User active/inactive status is managed through user update endpoint.
- Route-level role restrictions are enforced.

2. Financial Records Management
- Create/list/update/delete endpoints are implemented.
- Filtering by date/category/type and pagination are supported.

3. Dashboard Summary APIs
- Aggregated totals and trends are returned by summary endpoint.
- Includes category totals and recent activity.

4. Access Control Logic
- Central RBAC dependency enforces role access per endpoint.

5. Validation and Error Handling
- Input validation via schemas, plus consistent error responses.

6. Data Persistence
- Persistent PostgreSQL storage via SQLAlchemy async engine.

## Assumptions

- First admin is created through bootstrap endpoint before normal secured flows.
- Admin can manage all records.
- Analyst can read records and summaries.
- Viewer can read summaries only.

## Notes

- DB tables are auto-created at startup (`create_all`) for assignment simplicity.
- For production, migrations (`alembic`) should be used for schema changes.

## GitHub Push Safety Checklist

Before pushing:

1. Ensure `.env` is ignored and not staged.
2. Keep only `.env.example` in the repository.
3. Confirm logs and local DB files are ignored by `.gitignore`.
4. Rotate any previously exposed credentials before push.

Recommended commands:

```bash
git rm --cached .env
git add .gitignore .env.example README.md
git status
```
