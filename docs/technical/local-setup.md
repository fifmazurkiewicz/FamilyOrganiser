# Local setup

**Last updated:** 2026-09-07

Run FamilyOrganiser on a laptop **without Docker Desktop** and without deploying to Vercel/Render. Production stack is documented in [platform-architecture.md](../deployment/platform-architecture.md).

## Checklist

| Step | Command / check |
|------|-----------------|
| 1. Env templates | Copy `.env.example` → `.env` (repo root or `backend/`). Copy `frontend/.env.example` → `frontend/.env` if you need Supabase login. |
| 2. Database | Native Postgres on `localhost:5432` **or** a Supabase Cloud dev project. Do not use the production pooler URL locally. |
| 3. Backend | Poetry in `backend/` — see below. |
| 4. Frontend | npm in `frontend/` — Vite on port 3000, proxy `/api` → `:8000`. |
| 5. Smoke | `GET http://localhost:8000/api/health` → `{"status":"ok","service":"FamilyOrganiser API"}`. Open `http://localhost:3000`. |

Docker Compose is **optional** (`docker compose up`), not the default path.

## Backend (`backend/`)

```bash
cd backend
poetry install
# Set DATABASE_URL in .env (loaded from backend/ and repo root)
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

Local `DATABASE_URL` examples (placeholders only):

- Postgres: `postgresql+asyncpg://postgres:your-password@127.0.0.1:5432/familyorganiser`
- SQLite (legacy local fallback in `.env.example`): `sqlite+aiosqlite:///./familyorg.db`

CORS locally: `http://localhost:3000` (see `CORS_ORIGINS_STR` in `.env.example`).

Dev auth: email/password legacy works only when `SUPABASE_*` is unset. **Disabled in production** when Supabase env is set.

## Frontend (`frontend/`)

```bash
cd frontend
npm install
npm run dev
```

Leave `VITE_API_URL` **empty** so the Vite proxy and LAN/mobile clients hit this machine’s `/api`, not the phone’s localhost.

For Supabase login locally, set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` (anon/publishable only).

## Health

Same contract as Render:

- `GET /api/health` — liveness, no DB
- `GET /api/health/ready` — DB ping, `503` when degraded

## New env vars

When you add a variable: update `.env.example` / `frontend/.env.example` and this page in the same change.
