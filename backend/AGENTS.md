# Backend

FastAPI + Poetry. Production: Render Docker Web Service (`api-family.fmazurkiewicz.dev`).

## Commands

```bash
poetry install
poetry run pytest -q
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

Health: `GET /api/health` (liveness), `GET /api/health/ready` (DB). Verify Supabase JWT with PyJWT/JWKS — do not use `supabase-py`. `DATABASE_URL` locally is `localhost:5432` (or SQLite fallback); production uses the Supabase pooler.
