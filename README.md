# FamilyOrganiser

Aplikacja webowa do organizacji życia rodzinnego: wspólne listy zakupów, zadania, budżet miesięczny, inwestycje i raporty.

**Produkcja (live):**

| Co | Gdzie |
|----|--------|
| Aplikacja | [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev) |
| API | [api-family.fmazurkiewicz.dev](https://api-family.fmazurkiewicz.dev/api/health) |
| Auth + baza | Supabase (managed Postgres + Auth) |

Pełna dokumentacja: [`docs/README.md`](docs/README.md) · handover: [`docs/business/production-handover.md`](docs/business/production-handover.md)

---

## Stack

| Warstwa | Technologia |
|---------|-------------|
| Frontend | React 18, TypeScript, Vite, Tailwind — **Vercel** |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic — **Hetzner (Docker + Caddy)** |
| Baza | PostgreSQL (Supabase) |
| Auth | Supabase (magic link + Google OAuth) → JWT weryfikowany przez API |
| Deploy API | GitHub Actions → SSH → `scripts/deploy.sh` |

**Nie używamy:** Redis, Fly.io (archiwum w `archive/fly/`), Coolify na produkcji.

---

## Szybki start lokalny

### Docker Compose (zalecane)

```bash
git clone <repo-url>
cd FamilyOrganiser
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000  
- Swagger: http://localhost:8000/docs  

### Bez Dockera (Poetry + npm)

**Backend** (`backend/`):

```bash
cd backend
poetry install
cp ../.env.example .env   # ustaw DATABASE_URL na lokalny Postgres lub Supabase
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

**Frontend** (`frontend/`):

```bash
cd frontend
npm install
cp .env.example .env      # opcjonalnie Supabase — do logowania
npm run dev               # http://localhost:3000, proxy /api → :8000
```

---

## Zmienne środowiskowe

### Frontend (`frontend/.env` lub Vercel)

| Zmienna | Lokalnie | Produkcja (Vercel) |
|---------|----------|---------------------|
| `VITE_API_URL` | puste (proxy Vite) | `https://api-family.fmazurkiewicz.dev` |
| `VITE_SUPABASE_URL` | URL projektu Supabase | j.w. |
| `VITE_SUPABASE_ANON_KEY` | klucz **anon** (publiczny) | j.w. |

Po zmianie env na Vercel: **Redeploy** (zmienne `VITE_*` wchodzą tylko przy buildzie).

### Backend (`.env` na VPS / GitHub Secrets)

Szablon: `.env.example`. Produkcja: GitHub Actions zapisuje `.env` na Hetznerze — nie commituj sekretów.

Kluczowe: `DATABASE_URL` (session pooler Supabase `:5432`), `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `CORS_ORIGINS_STR`, `ADMIN_EMAIL`.

Szczegóły: [`docs/deployment/platform-architecture.md`](docs/deployment/platform-architecture.md)

---

## Struktura monorepo

```
FamilyOrganiser/
├── frontend/          # React SPA → Vercel (Root Directory: frontend)
├── backend/           # FastAPI → Docker na Hetzner
├── docker/            # Caddyfile, nginx (dev), entrypoint
├── scripts/deploy.sh  # Deploy API na VPS
├── .github/workflows/ # CI/CD backendu
├── docs/              # Dokumentacja biznes + tech + deploy
└── archive/fly/       # PoC Fly.io (nie produkcja)
```

---

## Trasy aplikacji (zalogowany użytkownik)

Wszystkie pod prefiksem `/app/`:

| Ścieżka | Moduł |
|---------|--------|
| `/app` | Dashboard |
| `/app/shopping` | Lista zakupów |
| `/app/tasks` | Zadania |
| `/app/budget-monthly` | Budżet miesięczny |
| `/app/investments` | Inwestycje |
| `/app/reports` | Raporty |
| `/app/groups` | Grupy rodzinne |
| `/app/profile` | Profil |
| `/app/admin` | Panel admina (tylko `is_app_admin`) |

Logowanie: `/login` → Supabase (Google / magic link) → `/auth/callback` → `/app`.

---

## Dev vs produkcja

| | Lokalnie | Produkcja |
|---|----------|-----------|
| Auth | Supabase (jeśli `VITE_SUPABASE_*`) lub legacy email/hasło | Supabase |
| Admin | `ADMIN_EMAIL` w `.env` | ten sam email po OAuth → `is_app_admin` |
| Legacy hasło | Działa bez Supabase (dev) | Wyłączone gdy `SUPABASE_*` ustawione |

Domyślne konto seed (tylko dev bez Supabase): `admin@admin.com` / `admin` — **nie używać na produkcji**.

---

## Deploy

- **Frontend:** push na `main` → Vercel buduje automatycznie (`frontend/`).
- **Backend:** push na `main` (ścieżki `backend/**`, Docker, workflow) → GitHub Actions → Hetzner.

Ręcznie: GitHub → Actions → **Deploy API (Hetzner)** → Run workflow.

---

## Licencja / właściciel

Prywatny projekt rodzinny — repozytorium prywatne.
