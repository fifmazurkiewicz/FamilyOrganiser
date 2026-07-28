# Architektura hostingu i deployu (decyzja)

**Status:** przyjęta  
**Data:** 2026-07-28  
**Ostatnia aktualizacja:** 2026-07-28  
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

### Env backendu (VPS / Compose)

| Zmienna | Uwagi |
|---------|--------|
| `DATABASE_URL` | `postgresql+asyncpg://…` z Supabase (nadpisuje SQLite z Dockerfile) |
| `SUPABASE_URL` | ten sam URL projektu |
| `SUPABASE_JWT_SECRET` | JWT Secret z Settings → API (weryfikacja HS256; alternatywa: JWKS) |
| `CORS_ORIGINS_STR` | `https://family.fmazurkiewicz.dev` |
| `ADMIN_EMAIL` | email admina (promocja `is_app_admin` po pierwszym logowaniu) |
| `PORT` | `8080` (domyślnie) |

---

## Deploy backendu (skrót)

Pliki w repo: `docker-compose.prod.yml`, `docker/Caddyfile`, root `Dockerfile` (API-only).

Na VPS (np. `/opt/apps/`): clone repo, `.env` z sekretami, `docker compose -f docker-compose.prod.yml up -d --build`.

Caddy terminuje TLS dla `api-family.fmazurkiewicz.dev` i proxy do `backend:8080`.

---

## Założenia operacyjne

1. Jedna apka = jedna subdomena FE (+ osobna subdomena API gdy własny backend).
2. Max ~5 osób na projekt.
3. Sekrety tylko w env Vercel / VPS — nie w git.
4. Fly.io pozostaje historycznym PoC.

---

## Powiązane dokumenty

- [Najtańszy hosting (VPS / porównanie)](cheap-hosting.md)
- [Fly.io (PoC)](fly-io.md)
- [Architektura aplikacji](../technical/architecture.md)
