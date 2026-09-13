# FamilyOrganiser

Monorepo: Vite + React frontend, FastAPI + Poetry backend.

## Stack (production)

Matches `.cursor/rules/deployment-standard.mdc`.

| Layer | Platform |
|---|---|
| Frontend | **Vercel** — `family.fmazurkiewicz.dev` (Root Directory `frontend`) |
| Backend | **Render** — Docker Web Service, `api-family.fmazurkiewicz.dev` |
| Database / auth | **Supabase** (managed Postgres + Auth). Backend verifies JWT (PyJWT / JWKS); no `supabase-py`. |

Do not document Hetzner, Coolify, or Fly.io as production. Fly.io and Hetzner leftovers are archive only.

## Commands

### Backend (`backend/`)

```bash
poetry install
poetry run pytest -q
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

### Frontend (`frontend/`)

```bash
npm install
npm run dev
npm run build
```

Local loop without Docker: [docs/technical/local-setup.md](docs/technical/local-setup.md). Health: `GET /api/health`.

## Learned user preferences

- Constitution language: assistant replies in **English**; product UI already in Polish is preserve.
- Prefer Cursor project rules in `.cursor/rules/` (alwaysApply) for durable guidance.
- Update `docs/` in the same session when infra, domain, hosting, or Supabase decisions settle.
- Prefer Poetry + npm locally over Docker Desktop.
- Commit / merge / push only when explicitly asked.
- Global skills (`ux-ui-challenger`, Taste, Superpowers) over duplicating long prompts per chat.
- Before significant UI/IA changes, spar with `ux-ui-challenger`.
- Full-project reviews: `code-reviewer`, `lead-architect`, `ux-ui-challenger`, `creative-strategist`, plus built-in `security-review`. Use `cloud-devops` only for explicit infra/deploy work.
- Folder `learning/` is tutor notes only — never commit (`.gitignore`).
- Infra/deploy: change repo code/config only; DNS, Supabase dashboard, Vercel env, and Render env stay as manual panel steps.

## Learned workspace facts

- Poetry/`pyproject.toml` live under `backend/`, not the repo root.
- Cloudflare DNS: `family` → Vercel; `api-family` should CNAME to `familyorganiser.onrender.com` (Render Docker Web Service, repo-root Dockerfile, branch `main`). If `GET /api/health` is not FamilyOrganiser JSON (`status`/`service`), the origin is wrong. Frontend Root Directory is `frontend`.
- Auth: frontend `@supabase/supabase-js`; backend SQLAlchemy/Alembic + JWT verify; provision `users.supabase_auth_id`.
- Vercel env: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (anon only — never `service_role`); `VITE_API_URL` or `frontend/vercel.json` rewrite of `/api/*` to `api-family.fmazurkiewicz.dev`.
- Authenticated routes are under `/app/...`. Sidebar: **Aplikacja** vs **Panel**. Theme toggle lives only in Profile.
- Local backend port 8000; Vite 3000 with `/api` proxy — leave `VITE_API_URL` empty for LAN/mobile.
- Core modules: family groups, shopping, tasks, monthly budget, investments, reports, notifications, app-admin.
- Access gate: `users.is_approved`. `/v1/users/me` allowed; other feature APIs return 403 `account_pending_approval`. Bootstrap owner `fifmazurkiewicz@gmail.com` (and `ADMIN_EMAIL`) is approved app-admin on every login. The waiting screen treats a failed `/v1/users/me` as pending, so a wrong or down API origin looks like an approval lockout.
- Backend settings load `.env` from `backend/` and repo root.
- Render **Free** compute has no Shell or one-off jobs — do not instruct Shell on Free. Workspace Starter billing does not unlock Shell until this service’s instance type is Starter and a deploy succeeds.
- `DATABASE_URL` on Render is the Supabase pooler (`*.pooler.supabase.com`), not `db.<ref>.supabase.co`. The app normalizes `postgresql://` to `postgresql+asyncpg://`.
- Known gaps: frontend **ApiPulse** not implemented (needed for Render Free cold start); leftover Hetzner compose/Caddy/`scripts/deploy.sh`; `docker/entrypoint.sh` does not run Alembic; 2026-07 product audit items (IDOR was later addressed in changelog — re-verify before assuming still open).
