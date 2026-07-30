# Audyt bezpieczeństwa — produkcja

**Data:** 2026-07-30  
**Zakres:** monorepo FamilyOrganiser (frontend Vercel + API Hetzner + Supabase)  
**Status ogólny:** ✅ **Akceptowalne dla prywatnej aplikacji rodzinnej** przy spełnieniu checklisty poniżej

---

## Podsumowanie w jednym akapicie

Sekrety nie są w repozytorium. Produkcja opiera się na Supabase Auth (Google / magic link) i weryfikacji JWT po stronie API. Frontend widzi tylko publiczny klucz anon. CORS ogranicza API do domeny frontu. Deploy zapisuje `.env` na VPS z uprawnieniami `600`. Nie znaleziono krytycznych luk w kodzie aplikacji; główne ryzyka to **higiena sekretów** i **silne hasła w panelach** (GitHub, Supabase, VPS).

---

## Checklist produkcyjna (Ty — ręcznie)

| # | Punkt | Status |
|---|--------|--------|
| 1 | `.env` / hasła **nie** w git | ✅ w repo tylko `.env.example` |
| 2 | Vercel: tylko `VITE_SUPABASE_ANON_KEY`, nie `service_role` | ⚠️ zweryfikuj w panelu |
| 3 | GitHub Secrets: `DATABASE_URL`, JWT, `SECRET_KEY`, SSH | ⚠️ trzymaj silne wartości |
| 4 | Supabase: Redirect URLs tylko Twoje domeny | ⚠️ bez `*` na cały internet |
| 5 | `CORS_ORIGINS_STR` = `https://family.fmazurkiewicz.dev` | ⚠️ bez wildcard |
| 6 | VPS: SSH kluczem, porty 22/80/443 | ⚠️ best practice |
| 7 | `ADMIN_EMAIL` = Twój rzeczywisty email | ⚠️ |
| 8 | Po zmianie env Vercel → redeploy | ✅ procedura znana |

---

## Findings

| Severity | Obszar | Opis | Rekomendacja |
|----------|--------|------|--------------|
| **Info** | Repo | Brak `.env`, brak `service_role` w kodzie | Utrzymuj; `.gitignore` obejmuje `.cursor/hooks/state/` |
| **Info** | Frontend | Token JWT w pamięci + localStorage (Zustand persist) | Standard SPA; wylogowanie czyści sesję |
| **Low** | Dev seed | `admin@admin.com` / `admin` w seed | Tylko lokalnie bez Supabase; na prod auth = Supabase |
| **Low** | Config defaults | `SECRET_KEY=changeme`, `ADMIN_PASSWORD=changeme` w `config.py` | Na prod wartości z GitHub Secrets, nie domyślne |
| **Low** | Legacy auth | Endpointy email/hasło nadal w API | Przy włączonym Supabase nie są główną ścieżką; OK |
| **Low** | SSL DB | `CERT_NONE` dla poolera Supabase | Typowe dla managed pooler; akceptowalne |
| **Low** | Client UI | Krótkie okno starego `is_app_admin` w localStorage | Backend i tak zwraca 403; bez wycieku danych |
| **Info** | `vercel.json` | Rewrite `/api` → Hetzner | Stały URL, nie open proxy; OK |
| **Info** | Deploy | `.env` na VPS `umask 077` | Dobre |

**Brak findings: Critical / High / Medium** w obecnym stanie kodu i konfiguracji repo.

---

## Auth — jak to działa bezpiecznie

```
Użytkownik → Supabase (login) → access_token (JWT)
                ↓
Frontend → Authorization: Bearer <token> → FastAPI
                ↓
API → weryfikacja JWT (JWKS / SUPABASE_JWT_SECRET)
                ↓
Provisioning użytkownika w Postgres (supabase_auth_id)
```

- Backend **nie** ufa samemu `localStorage` — każdy request chroniony tokenem.
- Admin panel: dodatkowo `is_app_admin` w DB + `get_current_app_admin`.

---

## Sekrety — gdzie trzymać

| Sekret | Gdzie | Nigdy |
|--------|-------|-------|
| `DATABASE_URL` | GitHub Secrets → VPS `.env` | git, frontend |
| `SUPABASE_JWT_SECRET` | GitHub Secrets | git, frontend |
| `VITE_SUPABASE_ANON_KEY` | Vercel env | OK publicznie |
| Supabase `service_role` | — | frontend, git |
| `HETZNER_SSH_KEY` | GitHub Secrets | git |

---

## CORS i nagłówki

- API: `CORSMiddleware` z listą z `CORS_ORIGINS_STR`
- Produkcja: jeden origin frontu (HTTPS)
- Token w nagłówku `Authorization` — nie cookie session → mniejsze ryzyko CSRF na API

---

## Baza danych

- Postgres Supabase; aplikacja przez SQLAlchemy (parametryzowane zapytania → ochrona przed SQL injection)
- Migracje: Alembic; deploy uruchamia `upgrade head`
- **Session pooler `:5432`** (nie transaction `:6543`) — stabilność, nie security issue

---

## Co monitorować

1. GitHub Actions — czy deploy przechodzi
2. `https://api-family.fmazurkiewicz.dev/api/health`
3. Supabase → Logs / Auth ( podejrzane logowania )
4. Vercel → Deployments po zmianach env

---

## Kiedy powtórzyć audyt

- Nowy moduł z uploadem plików / płatnościami
- Publiczna rejestracja bez zaproszeń
- Zmiana auth providera
- Dodanie webhooków z zewnętrznych serwisów

---

## Powiązane dokumenty

- [Architektura platformy](../deployment/platform-architecture.md)
- [Handover produkcyjny](../business/production-handover.md)
- Reguła repo: `.cursor/rules/secrets.mdc`
