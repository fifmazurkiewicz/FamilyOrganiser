# Architektura hostingu i deployu (decyzja)

**Status:** przyjęta  
**Data:** 2026-07-28  
**Ostatnia aktualizacja:** 2026-07-30  
**Zastępuje:** podejście „jedna apka na Fly.io” (zostaje w docs jako archiwum / PoC)

---

## Stan infrastruktury

| Zasób | Wartość |
|--------|---------|
| Domena | **fmazurkiewicz.dev** (Cloudflare DNS) |
| Frontend FamilyOrganiser | **family.fmazurkiewicz.dev** (Vercel, root `frontend/`) |
| Backend API | **api-family.fmazurkiewicz.dev** (Hetzner VPS, Docker + Caddy) |
| Supabase | managed Postgres + Auth (region wg projektu w panelu) |
| Schema aplikacji | tabele w Postgres Supabase (SQLAlchemy / Alembic) |
| Cloudflare Workers / D1 / R2 | nieużywane |

Subdomeny: `family` (FE), `api-family` (API); planowane: `www`, `tasks`, `rag`, `assistant`.

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
   (Vercel, static)       (Vercel FE)         (Hetzner: Caddy → :8080)
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
| Backend API | **Hetzner VPS + Docker Compose + Caddy** | FastAPI (obraz API-only, port 8080) |
| DNS / domena | **Cloudflare** | rejestrator + DNS |
| Baza / auth / pliki | **Supabase** (managed) | Postgres + Auth (magic link, Google) + pgvector |

**Bez Coolify** — świadomie: Compose + Caddy na VPS.  
**Bez Fly.io** w produkcji — `fly.toml` / PoC zostają jako archiwum.

### Dlaczego Supabase managed

- Rozdzielenie bazy od compute.
- Auth (magic link + Google OAuth) + automatyczne backupy.
- Backend łączy się connection stringiem (`DATABASE_URL`); JWT weryfikuje lokalnie (JWKS / JWT secret).

---

## Auth (docelowy model)

| Warstwa | Mechanizm |
|---------|-----------|
| Frontend | `@supabase/supabase-js` — `signInWithOtp`, `signInWithOAuth({ provider: 'google' })` |
| Backend | Weryfikacja `Authorization: Bearer` (Supabase JWT) + mapowanie / provisioning wiersza `users` |
| Env FE (Vercel) | `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (publishable) |
| Env BE (VPS) | `DATABASE_URL`, `SUPABASE_URL`, opcjonalnie `SUPABASE_JWT_SECRET`, `CORS_ORIGINS_STR` |

Supabase Dashboard → Authentication → URL Configuration:

- Site URL: `https://family.fmazurkiewicz.dev`
- Redirect URLs: `https://family.fmazurkiewicz.dev/**`

---

## Mapowanie projektów

| Projekt | Frontend | Backend | Dane |
|---------|----------|---------|------|
| Landing | Vercel | Nie | — |
| FamilyOrganiser | `family.fmazurkiewicz.dev` | `api-family.fmazurkiewicz.dev` | Supabase |
| RAG / asystent (plan) | Vercel | Coolify lub ten sam VPS | Supabase + pgvector |

### Env frontendu (Vercel)

| Zmienna | Wartość |
|---------|---------|
| `VITE_API_URL` | `https://api-family.fmazurkiewicz.dev` |
| `VITE_SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | anon / publishable key (publiczny) |

### Env backendu (źródło: GitHub Secrets → `.env` na VPS)

| Zmienna | Uwagi |
|---------|--------|
| `DATABASE_URL` | `postgresql+asyncpg://…` z Supabase |
| `SUPABASE_URL` | ten sam URL projektu |
| `SUPABASE_JWT_SECRET` | JWT Secret z Settings → API |
| `CORS_ORIGINS_STR` | `https://family.fmazurkiewicz.dev` |
| `ADMIN_EMAIL` | email admina (promocja `is_app_admin` po pierwszym logowaniu) |
| `PORT` | `8080` (domyślnie) |

---

## Deploy backendu — instrukcja krok po kroku

Cel: **family** (Vercel) + **api-family** (Hetzner). Sekrety w **GitHub Actions Secrets** (i Vercel dla FE). Nie commituj `.env`.

Pliki: `docker-compose.prod.yml`, `docker/Caddyfile`, `Dockerfile`, `scripts/deploy.sh`, `.github/workflows/deploy.yml`.

### Krok 1 — DNS (Cloudflare)

1. Wejdź w DNS domeny `fmazurkiewicz.dev`.
2. Dodaj rekord **A**: nazwa `api-family`, wartość = publiczne IPv4 serwera Hetzner.
3. Proxy: na start **DNS only** (szara chmura), żeby Caddy dostał Let’s Encrypt.
4. Poczekaj, aż `api-family.fmazurkiewicz.dev` wskazuje na IP VPS.

### Krok 2 — Klucz SSH pod GitHub Actions

Na komputerze:

```bash
ssh-keygen -t ed25519 -f hetzner_deploy -C "github-actions-familyorganiser" -N ""
```

- `hetzner_deploy` — prywatny → GitHub Secret `HETZNER_SSH_KEY`
- `hetzner_deploy.pub` — publiczny → VPS `authorized_keys`

### Krok 3 — VPS (Hetzner, raz)

1. Zainstaluj Docker, Compose plugin, `git`, `python3`, `curl`.
2. Sklonuj repo (deploy key / SSH z dostępem do prywatnego GitHub):

```bash
mkdir -p /opt/apps
cd /opt/apps
git clone git@github.com:fifmazurkiewicz/FamilyOrganiser.git
cd FamilyOrganiser
git checkout main
```

3. Dodaj treść `hetzner_deploy.pub` do `~/.ssh/authorized_keys` użytkownika workflow (`root` lub `deploy`), `chmod 600`.
4. User w grupie `docker` (albo root). Firewall: **22**, **80**, **443**.
5. Ścieżka `/opt/apps/FamilyOrganiser` = secret `HETZNER_APP_DIR`.

`.env` nie tworzysz ręcznie — powstanie przy pierwszym udanym deployu.

### Krok 4 — Secrets w GitHub

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret | Skąd / co |
|--------|-----------|
| `HETZNER_HOST` | IPv4 VPS |
| `HETZNER_USER` | user SSH (`root` / `deploy`) |
| `HETZNER_SSH_KEY` | cały PEM z `hetzner_deploy` |
| `HETZNER_APP_DIR` | `/opt/apps/FamilyOrganiser` |
| `DATABASE_URL` | Supabase URI z driverem `postgresql+asyncpg://` (często pooler `:6543`) |
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `SUPABASE_JWT_SECRET` | Supabase → Settings → API → JWT Secret |
| `CORS_ORIGINS_STR` | `https://family.fmazurkiewicz.dev` |
| `SECRET_KEY` | długi losowy string |
| `ADMIN_EMAIL` | Twój email admina |

Opcjonalnie: `SUPABASE_JWT_AUDIENCE` = `authenticated`.

### Krok 5 — Supabase Auth URLs

Authentication → URL Configuration:

- Site URL: `https://family.fmazurkiewicz.dev`
- Redirect URLs: `https://family.fmazurkiewicz.dev/**`

### Krok 6 — Vercel (frontend)

1. Root Directory = `frontend`, domena `family.fmazurkiewicz.dev`.
2. Env: `VITE_API_URL=https://api-family.fmazurkiewicz.dev`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
3. Redeploy.

### Krok 7 — Pierwszy deploy API

1. GitHub → **Actions** → **Deploy API (Hetzner)** → **Run workflow** (`main`).
2. Po sukcesie otwórz: `https://api-family.fmazurkiewicz.dev/api/health` → `{"status":"ok",...}`.

### Krok 8 — Na co dzień

- Push na `main` (backend/Docker) → auto-deploy.
- Albo ręcznie: Run workflow.
- Frontend: Vercel.

`deploy.sh`: pull → zapis `.env` z Secrets → `compose up --build` → `alembic upgrade` → health. Caddy → `:8080`, `restart: unless-stopped`.

### Diagnostyka

| Objaw | Sprawdź |
|-------|---------|
| SSH Permission denied | klucz, `authorized_keys`, user, port 22 |
| cd: no such file | `HETZNER_APP_DIR` |
| git pull failed | dostęp repo na VPS |
| Brak HTTPS | DNS only, 80/443, logi Caddy |
| CORS | `CORS_ORIGINS_STR` |
| 401 API | `SUPABASE_JWT_SECRET` / URL |

---

## Założenia operacyjne

1. Jedna apka = jedna subdomena FE (+ osobna subdomena API gdy własny backend).
2. Max ~5 osób na projekt.
3. Sekrety tylko w env Vercel / VPS / GitHub Actions secrets — nie w git.
4. Fly.io (`fly.toml`) pozostaje historycznym PoC — nie używamy w produkcji.

---

## Powiązane dokumenty

- [Najtańszy hosting (VPS / porównanie)](cheap-hosting.md)
- [Fly.io (PoC)](fly-io.md)
- [Architektura aplikacji](../technical/architecture.md)
