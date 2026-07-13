# FamilyOrganiser

Aplikacja do zarządzania finansami rodzinnymi. Backend (FastAPI + PostgreSQL + Redis) i frontend (React + TypeScript + Vite + Tailwind).

## Wymagania

- **Docker** + **Docker Compose** (zalecane)
- Lub lokalnie: **Python 3.12+**, **Poetry**, **Node.js 20+**, **PostgreSQL 16+**, **Redis 7+**

## Szybki start (Docker Compose)

```bash
# 1. Sklonuj repozytorium
git clone <repo-url>
cd FamilyOrganiser

# 2. Skopiuj plik konfiguracyjny i dostosuj wartości
cp .env.example .env

# 3. Uruchom wszystkie usługi
docker compose up --build
```

Aplikacja będzie dostępna pod:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API docs (Swagger):** http://localhost:8000/docs
- **Proxy (nginx):** http://localhost:80

## Uruchomienie lokalne (dev)

### Backend

```bash
cd backend

# Zainstaluj Poetry (jeśli nie masz)
pip install poetry

# Zainstaluj zależności
poetry install
# ...lub bez Poetry, przez pip:
# pip install -r requirements.txt

# Skopiuj .env do katalogu backend (lub ustaw zmienne środowiskowe)
cp ../.env.example .env
# Edytuj .env — ustaw DATABASE_URL na lokalny PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://familyorg:familyorg@localhost:5432/familyorg

# Uruchom migracje (jeśli istnieją)
poetry run alembic upgrade head

# Uruchom serwer deweloperski
poetry run uvicorn app.main:app --reload --port 8000
```

### Frontend

**Wymagania:** Node.js 20+ (zalecane LTS), npm lub pnpm

```bash
cd frontend

# Zainstaluj zależności
npm install

# Uruchom serwer deweloperski
npm run dev
```

Frontend uruchomi się na **http://localhost:3000**. Vite proxy'uje `/api` na backend (domyślnie `http://localhost:8000`).

**Uwaga:** Backend musi być uruchomiony przed frontendem (np. w osobnym terminalu), aby logowanie i API działały poprawnie.

**Dostępne skrypty:**

| Skrypt | Opis |
|--------|------|
| `npm run dev` | Serwer deweloperski z hot-reload |
| `npm run build` | Produkcyjny build (wynik w `dist/`) |
| `npm run preview` | Podgląd buildu produkcyjnego |

**Zmienna środowiskowa dla frontendu:**

Vite wczytuje zmienne z pliku `frontend/.env` lub `frontend/.env.local`. Skopiuj szablon:

```bash
cp frontend/.env.example frontend/.env
```

Domyślnie proxy kieruje `/api` na `http://localhost:8000`. Przy Docker Compose (frontend w kontenerze) ustaw np. `VITE_API_URL=http://localhost:80`.

## Baza danych

Przy pierwszym uruchomieniu backend automatycznie tworzy tabele w PostgreSQL, seeduje domyślne kategorie transakcji oraz konto administratora:

- **Email:** `admin@admin.com`
- **Hasło:** `admin`

Aby wygenerować nową migrację Alembic:

```bash
cd backend
poetry run alembic revision --autogenerate -m "opis zmiany"
poetry run alembic upgrade head
```

## Struktura projektu

```
FamilyOrganiser/
├── backend/                 # FastAPI REST API
│   ├── app/
│   │   ├── api/             # Endpointy HTTP (v1)
│   │   ├── core/            # Konfiguracja, bezpieczeństwo, wyjątki
│   │   ├── db/              # Silnik SQLAlchemy, sesja
│   │   ├── middleware/      # Middleware logowania
│   │   ├── models/          # Modele ORM (SQLAlchemy)
│   │   ├── repositories/    # Wzorzec repozytorium (dostęp do danych)
│   │   ├── schemas/         # Schematy Pydantic (walidacja)
│   │   ├── services/        # Logika biznesowa
│   │   └── tasks/           # Zadania cykliczne (APScheduler)
│   ├── alembic/             # Migracje bazy danych
│   ├── pyproject.toml       # Konfiguracja Poetry
│   └── Dockerfile
├── frontend/                # React + TypeScript + Vite
│   ├── src/
│   │   ├── api/             # Klient HTTP (Axios)
│   │   ├── components/      # Komponenty UI (layout, ui)
│   │   ├── features/        # Moduły funkcjonalne
│   │   ├── hooks/           # Custom hooks (React Query)
│   │   ├── lib/api/         # Serwisy API per moduł
│   │   ├── pages/           # Strony routingu
│   │   ├── router/          # React Router
│   │   ├── stores/          # Stan globalny (Zustand)
│   │   ├── types/           # Typy TypeScript
│   │   └── utils/           # Narzędzia pomocnicze
│   ├── package.json
│   └── Dockerfile
├── docker/                  # Konfiguracja nginx
├── docker-compose.yml
└── .env.example
```

## Architektura

### Backend — Clean Architecture

```
HTTP Request → API Endpoint → Service → Repository → Database
                   ↓              ↓
              Pydantic Schema   SQLAlchemy Model
```

- **API Endpoints** — obsługa HTTP, walidacja wejścia, autoryzacja (JWT)
- **Services** — logika biznesowa, orkiestracja operacji
- **Repositories** — generyczny wzorzec dostępu do danych (CRUD)
- **Models** — definicje tabel (SQLAlchemy ORM)
- **Schemas** — walidacja i serializacja danych (Pydantic)

### Frontend — Feature-based Architecture

```
Page → Feature Component → Custom Hook → API Service → HTTP Client
                              ↓
                         Zustand Store (stan globalny)
```

- **Pages** — strony routingu (cienka warstwa)
- **Features** — komponenty per moduł (listy, formularze, panele)
- **Hooks** — React Query hooks (cache, mutacje)
- **lib/api/** — typowane serwisy API per domena
- **Stores** — Zustand (auth, aktywna grupa)

## Zmienne środowiskowe

Plik `.env.example` zawiera wszystkie wymagane zmienne. Skopiuj go do `.env` i dostosuj wartości:

| Zmienna | Opis | Domyślna |
|---------|------|----------|
| `POSTGRES_USER` | Użytkownik PostgreSQL | `familyorg` |
| `POSTGRES_PASSWORD` | Hasło PostgreSQL | `changeme` |
| `POSTGRES_DB` | Nazwa bazy danych | `familyorg` |
| `DATABASE_URL` | Pełny URL do bazy (async) | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL do Redis | `redis://localhost:6379/0` |
| `SECRET_KEY` | Klucz do JWT | (zmień w produkcji!) |
| `CORS_ORIGINS_STR` | Dozwolone originy CORS (po przecinku) | `http://localhost:3000,http://localhost:80` |
| `VITE_API_URL` | URL backendu dla frontendu | `http://localhost:8000` |

## Technologie

**Backend:** FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Redis, Alembic, APScheduler, Pydantic v2, Poetry

**Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Radix UI, React Query, Zustand, React Router, Recharts

## Zasady utrzymania kodu

Projekt jest utrzymywany hobbystycznie — prostota ma pierwszeństwo (szczegóły: `BUSINESS_REQUIREMENTS.md`, sekcja 4.5):

- Komponenty frontendu **nie wykonują bezpośrednich wywołań HTTP** — zawsze przez typowane serwisy z `src/lib/api/` (jeden moduł na domenę: `auth`, `accounts`, `transactions`, …)
- Po operacjach zmieniających stan finansów (transakcje, przychody) widoki odświeża wspólny pomocnik `src/hooks/invalidate.ts` — nie kopiuj bloków `invalidateQueries`
- Listy w backendzie pobieraj jednym zapytaniem z JOIN-em (bez pętli zapytań per rekord) — wzorce w `app/repositories/family.py`
- Nieużywany kod usuwaj od razu

## Historia refaktoryzacji

**2026-07-13**

- **Przywrócono warstwę API frontendu** — katalog `frontend/src/lib/api/` (11 modułów serwisów) nigdy nie trafił do repozytorium, bo pasował do reguły `lib/` w `.gitignore` (szablon Pythona). Bez niego frontend się nie kompilował. Reguła została ograniczona wyjątkiem `!frontend/src/lib/`.
- **Ujednolicono odświeżanie danych** — powtarzany w wielu miejscach blok unieważniania zapytań React Query zastąpiono pomocnikiem `invalidateFinanceViews`.
- **`Layout.tsx` korzysta z serwisów API** zamiast surowych wywołań axios (typowanie zamiast `any`).
- **Usunięto zapytania N+1** w module grup rodzinnych (lista grup z liczbą członków oraz lista członków z danymi użytkowników — po jednym zapytaniu SQL).
- **Uzupełniono `backend/requirements.txt`** o `pydantic[email]` (bez tego instalacja przez pip nie uruchamiała aplikacji; instalacja przez Poetry nie była dotknięta).
- Usunięto martwy kod (nieużywane metody repozytoriów, przestarzałe fallbacki pól dashboardu) i dodano brakujący `src/vite-env.d.ts`.
