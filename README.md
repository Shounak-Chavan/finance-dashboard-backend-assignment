# Finance Data Processing and Access Control Backend

## Objective
This project is a backend implementation for a finance dashboard system. It is designed to demonstrate practical backend engineering skills in API design, data modeling, business logic, role-based access control, validation, and persistence.

The implementation prioritizes correctness, maintainability, and clear separation of concerns.

## Assignment Context
This submission maps to the assignment: Finance Data Processing and Access Control Backend.

The solution includes:
- Role-based user access management
- Financial records CRUD with soft delete
- Summary analytics APIs
- JWT authentication
- Input validation and structured error responses
- Async database persistence with migration support

## Tech Stack
- Python 3.10+
- FastAPI
- SQLAlchemy 2.0 (Async)
- PostgreSQL via asyncpg
- Alembic
- Pydantic v2
- JWT (python-jose)
- Passlib bcrypt
- SlowAPI (rate limiting)
- Pytest

## Architecture and Project Structure
- backend/main.py: app startup, middleware, router registration, lifespan hooks
- backend/api/routes/: route layer (auth, users, records, summary)
- backend/api/dependencies.py: current user resolution from bearer token
- backend/api/rbac.py: reusable role guard
- backend/services/: business logic and DB interactions
- backend/models/: SQLAlchemy models
- backend/schemas/: Pydantic request and response models
- backend/db/session.py: async engine and session factory
- backend/db/seed.py: initial admin seeding
- backend/core/: config, security, exception handlers, logging, rate limiter
- alembic/: migration configuration and revision history
- tests/: integration-style API tests with in-memory SQLite

## Project File Structure
```text
Project/
|-- alembic/
|   |-- versions/
|   |   `-- 1ec7314b947f_initial_tables.py
|   |-- env.py
|   |-- README
|   `-- script.py.mako
|-- backend/
|   |-- api/
|   |   |-- __init__.py
|   |   |-- middleware/
|   |   |   |-- __init__.py
|   |   |   `-- request_logger.py
|   |   |-- routes/
|   |   |   |-- __init__.py
|   |   |   |-- auth_routes.py
|   |   |   |-- finance_routes.py
|   |   |   |-- summary_routes.py
|   |   |   `-- user_routes.py
|   |   |-- dependencies.py
|   |   `-- rbac.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- exceptions.py
|   |   |-- logging_config.py
|   |   |-- rate_limiter.py
|   |   `-- security.py
|   |-- db/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- seed.py
|   |   `-- session.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- finance.py
|   |   `-- user.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- finance.py
|   |   `-- user.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- finance_service.py
|   |   |-- summary_service.py
|   |   `-- user_service.py
|   `-- main.py
|-- logs/
|-- tests/
|   |-- conftest.py
|   `-- test_finance_features.py
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- pyproject.toml
|-- README.md
`-- requirements.txt
```

## Data Model
### User
- id
- name
- email (unique)
- hashed_password
- role (admin, analyst, viewer)
- is_active
- created_at

### FinancialRecord
- id
- user_id (FK to users.id)
- amount
- type (income, expense)
- category
- date
- note
- is_deleted
- deleted_at
- created_at

## Role Model and Access Rules
Roles implemented:
- viewer
- analyst
- admin

Current permission behavior in this implementation:
- Admin:
  - Create users
  - List users
  - Update users
  - Create, update, delete financial records
  - Read records
  - Read summary
- Analyst:
  - Read records
  - Read summary
- Viewer:
  - Read records
  - Read summary

Notes:
- Access is enforced at backend route level through RBAC dependencies.
- Inactive users are blocked from protected endpoints.

## Authentication Flow
1. App startup seeds a default admin user from environment configuration if no admin exists.
2. Client logs in via POST /auth/login using form data:
   - username: user email
   - password: plain password
3. Server returns bearer JWT token.
4. Protected routes require Authorization: Bearer <token>.

## API Endpoints
### Auth
- POST /auth/login

### Example Login
POST /auth/login

Form Data:
- username: admin@example.com
- password: admin123

Response:
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

### Users (admin only)
- POST /users/
- GET /users/
- PUT /users/{user_id}

### Financial Records
- POST /records/ (admin)
- GET /records/ (admin, analyst, viewer)
  - Implemented query params in route: skip, limit
- PUT /records/{record_id} (admin)
- DELETE /records/{record_id} (admin)
  - Soft delete sets is_deleted = true and deleted_at timestamp

### Example Create Record
POST /records/

Headers:
- Authorization: Bearer <TOKEN>

Body:
```json
{
  "amount": 1000,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01"
}
```

Curl:
```bash
curl -X POST "http://127.0.0.1:8000/records/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"amount":1000,"type":"income","category":"salary","date":"2026-04-01"}'
```

### Summary
- GET /summary/ (admin, analyst, viewer)
  - Returns:
    - total_income
    - total_expense
    - net_balance

## Validation and Error Handling
Validation:
- Pydantic schema validation for request payloads
- Amount must be greater than 0
- Category length constraints
- Email format validation

Error handling:
- 401 for invalid credentials or invalid/expired token
- 403 for unauthorized roles or inactive users
- 404 for missing resources
- 429 for rate-limit breaches
- Global exception handlers for consistent JSON responses

## Data Persistence
- Primary persistence: PostgreSQL with async SQLAlchemy engine
- Database schema management: Alembic migrations
- Test persistence: in-memory SQLite for isolated test runs

## Optional Enhancements Included
- JWT authentication
- Soft delete for records
- Pagination parameters for listing records (skip, limit)
- Rate limiting middleware
- Structured request logging
- Integration-style automated tests
- Auto-generated API docs via Swagger

## Setup and Run
### 1. Create virtual environment
Windows PowerShell:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment (.env)
Minimum required keys:
- APP_NAME
- ACCESS_TOKEN_SECRET_KEY
- ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- DATABASE_URL
- ADMIN_NAME
- ADMIN_EMAIL
- ADMIN_PASSWORD
- RATE_LIMIT_MAX_REQUESTS
- RATE_LIMIT_WINDOW_SECONDS

### 4. Apply migrations
```bash
alembic upgrade head
```

### 5. Start API
```bash
uvicorn backend.main:app --reload
```

Open Swagger docs:
- http://127.0.0.1:8000/docs

## Running Tests
```bash
pytest -q
```

### Test Results
All tests passing:

4 passed, 0 failed

Current tests verify:
- Login and token flow
- Record creation
- Record update/delete flow
- Soft delete behavior
- Summary totals (income, expense, net)

## Requirement Mapping (Assignment)
### 1. User and Role Management
Implemented:
- User creation, listing, and update
- Role assignment per user
- Active/inactive enforcement
- RBAC restrictions on routes

### 2. Financial Records Management
Implemented:
- Create, read, update, delete (soft delete)
- Record model includes amount, type, category, date, note
- Listing endpoint with pagination controls

### 3. Dashboard Summary APIs
Implemented:
- Total income
- Total expense
- Net balance

### 4. Access Control Logic
Implemented:
- Central role guard dependency
- Route-level permission checks by role

### 5. Validation and Error Handling
Implemented:
- Pydantic request validation
- Explicit HTTP status codes and structured JSON errors

### 6. Data Persistence
Implemented:
- PostgreSQL-backed async persistence
- Alembic migration workflow

## Assumptions and Tradeoffs
- Summary endpoint currently focuses on core totals (income, expense, net) for clarity and reliability.
- Search and advanced record filtering logic exists in service layer and can be exposed via additional route parameters/endpoints if required.
- Role policy allows viewer read access to records and summary in this implementation.

## Code Quality Notes
- Clear separation between route, service, and data layers
- Reusable dependencies for auth and role checks
- Async DB operations throughout
- Centralized config and exception handling

## Submission Notes
- This repository is the original implementation for assignment evaluation.
- If a deployed URL is required, include it in the submission form.
- Ensure secrets are rotated before sharing publicly.

## Future Improvements
- Add advanced analytics (category totals, trends)
- Add refresh tokens
- Add Docker support
- Add caching (Redis)

## Safety Checklist Before Submission
1. Confirm .env is not committed.
2. Rotate ACCESS_TOKEN_SECRET_KEY and database credentials if previously exposed.
3. Verify alembic upgrade head runs successfully.
4. Run pytest -q and confirm tests pass.
5. Validate key APIs in Swagger.
