## Learned User Preferences

- Respond in Polish unless the user explicitly asks for another language.
- Prefer Cursor project rules (`.cursor/rules/*.mdc` with `alwaysApply`) for durable guidance such as docs-on-infra changes and secrets handling; keep always-apply rules few and focused.
- Prefer updating existing docs in `docs/` in the same session when infrastructure, domain, hosting, or Supabase decisions become settled — do not wait for a separate “update docs” request.
- Prefer Poetry + npm local runs over Docker Desktop when the user wants to develop without Docker.
- Prefer committing and merging/pushing only when explicitly asked (e.g. “zmerguj do maina”, “zrób mr”).
- Global custom skills (`C:\Users\MSI\.cursor\skills\`) and subagents (`C:\Users\MSI\.cursor\agents\`) are for cross-project reuse; prefer them for specialized roles (e.g. `ux-ui-challenger`) rather than duplicating long prompts per chat.
- Before significant UI, layout, or navigation changes, prefer UX/UI sparring with the user (skill or subagent `ux-ui-challenger`) over jumping straight to implementation.
- Folder `learning/` is for tutor notes only and must never be committed (keep it in `.gitignore`).
- Prefer GitHub Actions auto-deploy for the Hetzner API (SSH + `scripts/deploy.sh`) over repeated manual VPS setup; keep deploy/backend secrets in GitHub Actions Secrets (never commit `.env`).
- For infra/deploy work, prefer agents to change only repo code/config; DNS, Supabase dashboard, Vercel env, and GitHub Secrets stay as manual panel steps.

## Learned Workspace Facts

- Monorepo: `frontend/` (Vite + React) and `backend/` (FastAPI + Poetry); Poetry/`pyproject.toml` live under `backend/`, not the repo root.
- Production domain is `fmazurkiewicz.dev` (Cloudflare DNS): `family` → Vercel frontend, `api-family` → Hetzner API (often DNS-only so Caddy can get Let’s Encrypt); frontend Root Directory is `frontend`.
- Production API is `api-family.fmazurkiewicz.dev` on Hetzner via `docker-compose.prod.yml` + Caddy (port 8080); Coolify is not the production path; deploy is GitHub Actions → SSH → `scripts/deploy.sh` (pull, compose build, alembic, health).
- Fly.io (`archive/fly/`, historical all-in-one image) is archive/PoC only — not the production hosting direction.
- Auth and DB target Supabase managed (Postgres + Auth: magic link and Google OAuth); frontend uses `@supabase/supabase-js`; backend does not use `supabase-py` — SQLAlchemy/Alembic to Postgres and verifies Supabase JWT (JWKS / JWT secret), provisioning `users` (including `supabase_auth_id`).
- Vercel frontend env: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (anon/publishable only — never `service_role`); API via `VITE_API_URL` or `frontend/vercel.json` rewrite of `/api/*` to `api-family.fmazurkiewicz.dev`.
- App routes for authenticated UI are under `/app/...` (e.g. `/app/shopping`, `/app/tasks`, `/app/budget-monthly`, `/app/profile`, `/app/admin`); sidebar links must use that prefix.
- Authenticated sidebar uses two bottom tabs: **Aplikacja** (family group + product modules including notifications) and **Panel** (profile, app admin, logout); theme toggle lives only in Profile.
- Local backend typically runs on port 8000; Vite frontend on 3000 with `/api` proxy — leave `VITE_API_URL` empty for LAN/mobile so the phone does not hit its own localhost.
- Core product modules: family groups, shopping lists, tasks, monthly budget, investments, reports, notifications, and an app-admin panel for users/groups.
- Backend settings should load `.env` from both `backend/` and the repo root so env is not hardcoded and root `.env` works when running from `backend/`.
