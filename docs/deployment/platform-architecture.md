# Architektura hostingu i deployu (decyzja)

**Status:** przyjęta  
**Data:** 2026-07-28  
**Ostatnia aktualizacja:** 2026-09-07  
**Zastępuje:** Hetzner VPS + Caddy (2026-07) oraz „jedna apka na Fly.io” (archiwum / PoC)

Kanoniczny stack (constitution): **Vercel + Render + Supabase**. Zob. `.cursor/rules/deployment-standard.mdc`.

---

## Stan infrastruktury

| Zasób | Wartość |
|--------|---------|
| Domena | **fmazurkiewicz.dev** (Cloudflare DNS) |
| Frontend FamilyOrganiser | **family.fmazurkiewicz.dev** (Vercel, root `frontend/`) |
| Backend API | **api-family.fmazurkiewicz.dev** (Render Docker Web Service) |
| Supabase | managed Postgres + Auth (region wg projektu w panelu) |
| Schema aplikacji | tabele w Postgres Supabase (SQLAlchemy / Alembic) |
| Cloudflare Workers / D1 / R2 | nieużywane |

Subdomeny: `family` (FE), `api-family` (API).

Render nadaje też hostname `*.onrender.com` (nazwa serwisu jest w panelu Render — nie commitujemy jej). Cloudflare **CNAME** `api-family` → ten hostname. Jeśli `GET /api/health` nie zwraca JSON `{"status":"ok",...}`, rekord DNS wskazuje zły origin.

---

## Architektura ogólna

- **Strona główna** = agregator / landing: statyczna na Vercel.
- **Każdy projekt** = osobny deployment pod subdomeną.
- **Skala:** do ~5 użytkowników na apkę — bez multi-tenancy.

```
                    Cloudflare (DNS + SSL edge)
                         fmazurkiewicz.dev
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   www.…                  family.…            api-family.…
   (Vercel, static)       (Vercel FE)         (Render Web Service)
                                │                    │
                                └────────┬───────────┘
                                         ▼
                                    Supabase
                              (Postgres, Auth, Storage, pgvector)
```

---

## Hosting / deploy

| Warstwa | Wybór | Rola |
|---------|--------|------|
| Frontend | **Vercel** | SPA Vite; Root Directory = `frontend` |
| Backend API | **Render** (Docker Web Service, Free na start) | FastAPI z root `Dockerfile`, port 8080 |
| DNS / domena | **Cloudflare** | rejestrator + DNS |
| Baza / auth / pliki | **Supabase** (managed) | Postgres + Auth (magic link, Google) + pgvector |

**Bez Hetzner / VPS, Coolify, Fly.io** w produkcji. Fly.io: historyczny PoC — [fly-io.md](fly-io.md). Hetzner: leftover w repo (`docker-compose.prod.yml`, Caddy, `scripts/deploy.sh`, archived workflow) — nie jest ścieżką prod.

### Dlaczego ten stack

- Niski, sporadyczny ruch — Render Free zamiast stałego VPS.
- Baza i auth oddzielone od compute (Supabase).
- Render obsługuje TLS i reverse proxy — obraz API **bez** Caddy w kontenerze.
- Kompromis: cold start 30–60 s po ~15 min bezczynności (plan Free).

### Dlaczego Supabase managed

- Rozdzielenie bazy od compute.
- Auth (magic link + Google OAuth) + automatyczne backupy Postgres (~co 30 dni).
- Backend łączy się connection stringiem (`DATABASE_URL`); JWT weryfikuje lokalnie (JWKS / JWT secret).

---

## Auth (docelowy model)

| Warstwa | Mechanizm |
|---------|-----------|
| Frontend | `@supabase/supabase-js` — `signInWithOtp`, `signInWithOAuth({ provider: 'google' })` |
| Backend | Weryfikacja `Authorization: Bearer` (Supabase JWT) + mapowanie / provisioning wiersza `users` |
| Env FE (Vercel) | `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (publishable) |
| Env BE (Render) | `DATABASE_URL`, `SUPABASE_URL`, opcjonalnie `SUPABASE_JWT_SECRET`, `CORS_ORIGINS_STR` |

Supabase Dashboard → Authentication → URL Configuration:

- Site URL: `https://family.fmazurkiewicz.dev`
- Redirect URLs: `https://family.fmazurkiewicz.dev/**`

---

## Mapowanie projektów

| Projekt | Frontend | Backend | Dane |
|---------|----------|---------|------|
| Landing | Vercel | Nie | — |
| FamilyOrganiser | `family.fmazurkiewicz.dev` | `api-family.fmazurkiewicz.dev` | Supabase |

### Env frontendu (Vercel)

| Zmienna | Wartość |
|---------|---------|
| `VITE_API_URL` | `https://api-family.fmazurkiewicz.dev` |
| `VITE_SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | anon / publishable key (publiczny) |

**Po zmianie env:** Redeploy na Vercel (zmienne `VITE_*` wchodzą tylko przy buildzie).

### `frontend/vercel.json`

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api-family.fmazurkiewicz.dev/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

- **SPA fallback** — React Router (`/app/*`, `/auth/callback`).
- **Proxy `/api`** — opcjonalny fallback gdy `VITE_API_URL` puste; **kanonicznie** ustaw `VITE_API_URL` na Vercel.

### Env backendu (źródło: panel Render → Environment)

| Zmienna | Uwagi |
|---------|--------|
| `DATABASE_URL` | `postgresql+asyncpg://…` przez **Supavisor / pooler** (nie `db.<ref>.supabase.co` — IPv6) |
| `SUPABASE_URL` | ten sam URL projektu |
| `SUPABASE_JWT_SECRET` | JWT Secret z Settings → API |
| `CORS_ORIGINS_STR` | `https://family.fmazurkiewicz.dev` (plus preview `*.vercel.app` gdy potrzeba) |
| `ADMIN_EMAIL` | email admina (promocja `is_app_admin` + `is_approved` przy logowaniu; bootstrap: `fifmazurkiewicz@gmail.com`) |
| `PORT` | `8080` (root `Dockerfile` / Render) |

Nie commituj `.env`. Render Free **nie ma** trwałego dysku — żadnego SQLite na produkcji.

---

## Deploy backendu — Render

Cel: **family** (Vercel) + **api-family** (Render). Sekrety w **panelu Render** i **Vercel** (FE). Nie commituj `.env`.

Pliki: root `Dockerfile` (API-only, `ca-certificates`, health `GET /api/health`), `docker/entrypoint.sh`.

### Krok 1 — Serwis Render

1. Render → New → **Web Service**, połącz repo GitHub `FamilyOrganiser`.
2. Runtime: **Docker**, Dockerfile path: `/Dockerfile` (kontekst = root repo).
3. Health check: `/api/health` (liveness, bez DB). Opcjonalnie `/api/health/ready` (ping DB).
4. Auto-deploy z gałęzi `main`.

### Krok 2 — DNS (Cloudflare)

1. DNS domeny `fmazurkiewicz.dev`.
2. Rekord **CNAME**: nazwa `api-family`, target = hostname Render (`<service>.onrender.com`).
3. Proxy Cloudflare wg potrzeby (Render i tak kończy TLS na swoim hostname).

### Krok 3 — Env w Render

| Zmienna | Skąd / co |
|--------|-----------|
| `DATABASE_URL` | Supabase URI z driverem `postgresql+asyncpg://` (pooler) |
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `SUPABASE_JWT_SECRET` | Supabase → Settings → API → JWT Secret |
| `CORS_ORIGINS_STR` | `https://family.fmazurkiewicz.dev` |
| `SECRET_KEY` | długi losowy string |
| `ADMIN_EMAIL` | `fifmazurkiewicz@gmail.com` |
| `PORT` | `8080` |

Opcjonalnie: `SUPABASE_JWT_AUDIENCE` = `authenticated`.

### Krok 4 — Supabase Auth URLs

Authentication → URL Configuration:

- Site URL: `https://family.fmazurkiewicz.dev`
- Redirect URLs: `https://family.fmazurkiewicz.dev/**`

### Krok 5 — Vercel (frontend)

1. Root Directory = `frontend`, domena `family.fmazurkiewicz.dev`.
2. Env: `VITE_API_URL=https://api-family.fmazurkiewicz.dev`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
3. Redeploy.

### Krok 6 — Smoke

1. Po deployu Render: `https://api-family.fmazurkiewicz.dev/api/health` → `{"status":"ok","service":"FamilyOrganiser API"}`.
2. Frontend: logowanie Google / magic link → `/app`.

### Krok 7 — Na co dzień

- Push na `main` (backend / Dockerfile) → Render auto-deploy.
- Frontend: Vercel.

Migracje: `docker/entrypoint.sh` obecnie tylko startuje uvicorn. Na Render ustaw start command albo rozszerz entrypoint o `alembic upgrade head` przed uvicorn — inaczej nowe migracje nie wejdą same.

### CI i backup bazy

| Workflow | Plik | Kiedy |
|----------|------|--------|
| **CI** | `.github/workflows/ci.yml` | push/PR na `main` — pytest + `npm run build` |
| **Backup Supabase** | `.github/workflows/backup-supabase.yml` | 1. dnia miesiąca 03:00 UTC + ręcznie; artefakt 90 dni |
| Skrypt lokalny | `scripts/backup-supabase.sh` | ten sam `pg_dump` co w Actions |
| **Deploy API (Hetzner)** | `.github/workflows/deploy.yml` | **archiwum** — tylko `workflow_dispatch`; produkcja = Render |

Szczegóły restore: [backup-restore.md](backup-restore.md).

### Diagnostyka

| Objaw | Sprawdź |
|-------|---------|
| Health nie JSON / obcy serwis | Cloudflare CNAME `api-family` → ten serwis Render |
| Cold start 30–60 s | Render Free po bezczynności; frontend powinien mieć ApiPulse (luka — jeszcze nie w kodzie) |
| CORS | `CORS_ORIGINS_STR` w Render |
| 401 API | `SUPABASE_JWT_SECRET` / URL |
| SSL do bazy | `DATABASE_URL` przez pooler; obraz ma `ca-certificates` |
| Migracje nie wchodzą | Alembic w start command / entrypoint |

### Znane luki vs constitution

- Frontend **nie** ma jeszcze wspólnego `ApiPulseProvider` / bannera „Waking up API…”.
- Leftover Hetzner: `docker-compose.prod.yml`, `docker/Caddyfile`, `scripts/deploy.sh`.

---

## Założenia operacyjne

1. Jedna apka = jedna subdomena FE + subdomena API na Render.
2. Max ~5 osób na projekt.
3. Sekrety tylko w env Vercel / Render — nie w git, nie na VPS.
4. Fly.io i Hetzner — historyczne; nie używamy w produkcji.
5. Lokalnie: bez Docker Desktop — [local-setup.md](../technical/local-setup.md).

---

## Powiązane dokumenty

- [Local setup](../technical/local-setup.md)
- [Najtańszy hosting (porównanie / archiwum VPS)](cheap-hosting.md)
- [Backup i restore](backup-restore.md)
- [GitBook — podłączenie](gitbook-setup.md)
- [Architektura aplikacji](../technical/architecture.md)
