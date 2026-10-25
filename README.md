# Car Dealership Inventory

A full-stack vehicle inventory management system built for a car
dealership. Customers can browse and purchase vehicles; admins can
manage stock.

## Stack

  Layer      Technology
  ---------- ------------------------------------------------
  Frontend   React 19 · TypeScript · Vite · Tailwind CSS v4
  Backend    Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic
  Auth       JWT (PyJWT) · Argon2 password hashing
  Database   PostgreSQL 16
  Testing    pytest · pytest-cov · mypy (strict) · ruff
  CI         GitHub Actions

------------------------------------------------------------------------

## Prerequisites

-   [Docker](https://docs.docker.com/get-docker/) --- runs PostgreSQL
-   [uv](https://docs.astral.sh/uv/getting-started/installation/) ---
    Python package manager
-   [Node.js 20+](https://nodejs.org/) --- for the frontend

------------------------------------------------------------------------

## 1 · Database

The project uses two PostgreSQL databases: one for development and one
for tests. Both run in a single Docker container.

``` bash
# Start the container (runs in the background, restarts on reboot)
docker run -d \
  --name dealership-db \
  --restart unless-stopped \
  -e POSTGRES_USER=dealership \
  -e POSTGRES_PASSWORD=dealership \
  -e POSTGRES_DB=dealership \
  -p 5433:5432 \
  postgres:16-alpine

# Create the test database
docker exec dealership-db \
  psql -U dealership -c "CREATE DATABASE dealership_test;"
```

To stop or remove the container later:

``` bash
docker stop dealership-db
docker rm dealership-db
```

------------------------------------------------------------------------

## 2 · Backend

### 2.1 Install dependencies

``` bash
cd backend
uv sync
```

### 2.2 Environment variables

``` bash
cp .env.example .env
```

The database defaults in `.env.example` should match the Docker
container above. Use a locally generated random value for `JWT_SECRET`.
Keep `.env` out of version control and never publish your secret.

  ---------------------------------------------------------------------------------------------------------------------------
  Variable                        Default                                                                       Description
  ------------------------------- ----------------------------------------------------------------------------- -------------
  `DATABASE_URL`                  `postgresql+psycopg://dealership:dealership@localhost:5433/dealership`        Dev DB

  `TEST_DATABASE_URL`             `postgresql+psycopg://dealership:dealership@localhost:5433/dealership_test`   Test DB

  `JWT_SECRET`                    `change-me-in-production`                                                     Secret used
                                                                                                                to sign JWTs
                                                                                                                --- change
                                                                                                                this

  `JWT_ALGORITHM`                 `HS256`                                                                       JWT signing
                                                                                                                algorithm

  `ACCESS_TOKEN_EXPIRE_MINUTES`   `60`                                                                          Token
                                                                                                                lifetime in
                                                                                                                minutes
  ---------------------------------------------------------------------------------------------------------------------------

### 2.3 Run migrations

``` bash
cd backend
uv run alembic upgrade head
```

### 2.4 Create an admin account

Public registration (`POST /api/auth/register`) creates customer
accounts. To create the initial administrator account, use the seed
script at `backend/scripts/seed_admin.py`.

From the `backend/` directory, first verify that `DATABASE_URL` in
`.env` points to the development database (`dealership`), not the test
database (`dealership_test`). Then run:

``` bash
read -r -p "Admin email: " ADMIN_EMAIL
read -r -s -p "Admin password: " ADMIN_PASSWORD
echo

export ADMIN_EMAIL ADMIN_PASSWORD
uv run python -m scripts.seed_admin

unset ADMIN_EMAIL ADMIN_PASSWORD
```

Enter the desired admin email and a password of at least 12 characters
when prompted. The password is hidden while typing. The script hashes it
using the project's existing Argon2 password hasher and creates the
account with the `admin` role.

The script is safe to rerun: if the admin account already exists, it
makes no changes. If the email belongs to an existing customer, it stops
rather than silently promoting that account. Keep credentials out of
source control and do not commit `.env`.

### 2.5 Start the dev server

``` bash
cd backend
uv run uvicorn app.main:create_app --factory --reload --port 8000
```

The API will be available at <http://localhost:8000>. Interactive docs:
<http://localhost:8000/docs>

------------------------------------------------------------------------

## 3 · Frontend

### 3.1 Install dependencies

``` bash
cd frontend
npm install
```

### 3.2 Start the dev server

``` bash
cd frontend
npm run dev
```

The app will be available at <http://localhost:5173>.

> The frontend expects the backend to be running at
> `http://localhost:8000`.

------------------------------------------------------------------------

## API reference

All routes under `/api/vehicles` and `/api/auth/me` require an
`Authorization: Bearer <token>` header. Obtain a token from
`POST /api/auth/login`.

### Auth

  Method   Path                   Auth   Description
  -------- ---------------------- ------ -----------------------------------
  `POST`   `/api/auth/register`   ---    Register a new customer account
  `POST`   `/api/auth/login`      ---    Login; returns a JWT bearer token
  `GET`    `/api/auth/me`         User   Current user profile

### Vehicles

  ------------------------------------------------------------------------
  Method          Path                     Auth            Description
  --------------- ------------------------ --------------- ---------------
  `GET`           `/api/vehicles`          User            List all
                                                           vehicles
                                                           (including
                                                           out-of-stock)

  `GET`           `/api/vehicles/search`   User            Filter by make,
                                                           model,
                                                           category, price
                                                           range

  `POST`          `/api/vehicles`          User            Create a new
                                                           vehicle listing

  `PUT`           `/api/vehicles/:id`      User            Update a
                                                           vehicle

  `DELETE`        `/api/vehicles/:id`      **Admin**       Remove a
                                                           vehicle listing
  ------------------------------------------------------------------------

### Inventory

  ---------------------------------------------------------------------------
  Method         Path                           Auth           Description
  -------------- ------------------------------ -------------- --------------
  `POST`         `/api/vehicles/:id/purchase`   User           Purchase a
                                                               quantity of a
                                                               vehicle

  `POST`         `/api/vehicles/:id/restock`    **Admin**      Add stock to a
                                                               vehicle
  ---------------------------------------------------------------------------

**Vehicle categories:** `sedan` · `suv` · `truck` · `van` · `coupe` ·
`hatchback` · `convertible` · `pickup`

------------------------------------------------------------------------

## Running tests

``` bash
cd backend

# Run the full test suite (unit + integration + API)
uv run pytest

# With verbose output
uv run pytest -v

# Lint and type-check
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

The test suite uses the `TEST_DATABASE_URL` database and rolls back
every transaction after each test, so the database is always left clean.

------------------------------------------------------------------------

## Project structure

``` text
.
├── backend/
│   ├── app/
│   │   ├── auth/          # Registration, login, /me
│   │   ├── vehicles/      # Vehicle CRUD and search
│   │   ├── inventory/    # Purchase and restock
│   │   ├── core/          # Config, security, deps, exceptions
│   │   └── db/            # SQLAlchemy base and session
│   ├── alembic/           # Database migrations
│   └── tests/
│       ├── unit/          # Pure logic (no DB)
│       ├── integration/   # Repository tests against real Postgres
│       └── api/           # End-to-end HTTP tests via TestClient
└── frontend/
    └── src/
```

------------------------------------------------------------------------

## CI

GitHub Actions runs on every push and pull request that touches
`backend/`. The pipeline:

1.  Installs dependencies (`uv sync --locked`)
2.  Lints with `ruff check` and `ruff format --check`
3.  Type-checks with `mypy --strict`
4.  Runs the full test suite with coverage

Test and coverage reports are uploaded as workflow artifacts on every
run.

## My AI Usage
### Tools Used

I used and Claude (Chat and agent) as AI-assisted development tools throughout this project.

I used AI to help explore the application architecture, evaluate implementation approaches, write unit and integration tests, implement backend functionality, and debug issues encountered during development. I also used it to discuss design decisions, improve code organization, and understand errors during local testing.

chats : https://claude.ai/share/cc52d893-bf76-46b8-911a-2a5c08a7ac7b
