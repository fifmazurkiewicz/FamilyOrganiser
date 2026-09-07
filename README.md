# FamilyOrganiser

Aplikacja webowa do organizacji życia rodzinnego: wspólne listy zakupów, zadania, budżet miesięczny, inwestycje i raporty.

**Produkcja (live):**

| Co | Gdzie |
|----|--------|
| Aplikacja | [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev) |
| API | [api-family.fmazurkiewicz.dev](https://api-family.fmazurkiewicz.dev/api/health) (Render) |
| Auth + baza | Supabase (managed Postgres + Auth) |

Pełna dokumentacja: [`docs/README.md`](docs/README.md) · handover: [`docs/business/production-handover.md`](docs/business/production-handover.md)

---

## Stack

| Warstwa | Technologia |
|---------|-------------|
| Frontend | React 18, TypeScript, Vite, Tailwind — **Vercel** |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic — **Render** (Docker Web Service) |
| Baza | PostgreSQL (Supabase) |
| Auth | Supabase (magic link + Google OAuth) → JWT weryfikowany przez API |
| Deploy API | Render auto-deploy z `main` (root `Dockerfile`) |

**Nie używamy na produkcji:** Redis, Hetzner/VPS, Fly.io (historyczny PoC), Coolify.

---

## Szybki start lokalny

**Domyślnie bez Dockera** (Poetry + npm). Szczegóły: [`docs/technical/local-setup.md`](docs/technical/local-setup.md).

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

Docker Compose jest **opcjonalny** (`docker compose up --build`) — nie jest wymagany do dev.

---

## Zmienne środowiskowe

### Frontend (`frontend/.env` lub Vercel)

| Zmienna | Lokalnie | Produkcja (Vercel) |
|---------|----------|---------------------|
| `VITE_API_URL` | puste (proxy Vite) | `https://api-family.fmazurkiewicz.dev` |
| `VITE_SUPABASE_URL` | URL projektu Supabase | j.w. |
| `VITE_SUPABASE_ANON_KEY` | klucz **anon** (publiczny) | j.w. |

Po zmianie env na Vercel: **Redeploy** (zmienne `VITE_*` wchodzą tylko przy buildzie).

### Backend (env w panelu Render)

Szablon: `.env.example`. Produkcja: zmienne w **Render → Environment** — nie commituj sekretów.

Kluczowe: `DATABASE_URL` (Supabase **pooler / Supavisor**), `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `CORS_ORIGINS_STR`, `ADMIN_EMAIL`.

Szczegóły: [`docs/deployment/platform-architecture.md`](docs/deployment/platform-architecture.md)

---

## Struktura monorepo

```
FamilyOrganiser/
├── frontend/          # React SPA → Vercel (Root Directory: frontend)
├── backend/           # FastAPI → Render (root Dockerfile)
├── docker/            # entrypoint; leftover Caddy/nginx (nie prod)
├── .github/workflows/ # CI, backup Supabase; Hetzner deploy = archiwum
├── docs/              # Dokumentacja (+ GitBook: .gitbook.yaml)
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
| Admin | `ADMIN_EMAIL` / bootstrap owner email | ten sam email po OAuth → `is_app_admin` + `is_approved` |
| Legacy hasło | Działa bez Supabase (dev) | Wyłączone gdy `SUPABASE_*` ustawione |

Domyślne konto seed (tylko dev bez Supabase): `admin@admin.com` / `admin` — **nie używać na produkcji**.

---

## Deploy

- **Frontend:** push na `main` → Vercel buduje automatycznie (`frontend/`).
- **Backend:** push na `main` → Render auto-deploy (Docker Web Service).

Hostowanie: [`docs/deployment/platform-architecture.md`](docs/deployment/platform-architecture.md).

---

## Licencja / właściciel

Prywatny projekt rodzinny — repozytorium prywatne.
