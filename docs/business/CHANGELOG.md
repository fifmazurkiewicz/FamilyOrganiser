# Lista zmian (CHANGELOG)

## [2.4] — 2026-09-07 — Hosting Render + constitution

- Produkcja API: **Render** (Docker Web Service), nie Hetzner/Caddy
- Docs i `AGENTS.md` zgodne z `deployment-standard.mdc` (Vercel + Render + Supabase)
- Cursor: Graft MCP, spec-driven docs, Taste dials, env-secrets, Superpowers w `.cursor/rules/`
- Local setup bez Dockera: `docs/technical/local-setup.md`
- Workflow Hetzner: archiwum (`workflow_dispatch` only)

## [2.3] — 2026-09-07 — Approval gate

- Nowa flaga `users.is_approved` (osobno od `is_active` / `is_locked`)
- Nowe konta czekają na akceptację; istniejące grandfathered
- `ADMIN_EMAIL` + bootstrap owner `fifmazurkiewicz@gmail.com` → `is_approved` + `is_app_admin` przy każdym logowaniu
- Feature API: 403 `account_pending_approval`; `/users/me` działa bez akceptacji
- Admin: Akceptuj / Cofnij dostęp (bez self-revoke, bez powiadomień)
- Frontend: ekran oczekiwania, bez chrome `/app/*`

## [2.2] — 2026-07-30 — Produkcja

### 🔒 Bezpieczeństwo i jakość (sesja hardening)

- **IDOR:** wymuszanie członkostwa w grupie we wszystkich modułach danych
- **Powiadomienia:** eventy zakupów i zadań (bez reminderów cyklicznych)
- **Legacy auth:** wyłączone na prod (Supabase JWT)
- **CI:** pytest + build frontendu na push/PR
- **Backup Supabase:** miesięczny pg_dump (1. dnia miesiąca, artefakt 90 dni)

### 🚀 Wdrożenie produkcyjne

- **Frontend live:** [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev) (Vercel)
- **API live:** [api-family.fmazurkiewicz.dev](https://api-family.fmazurkiewicz.dev) (wtedy Hetzner + Caddy; od 2026-09-07: Render)
- **Auth:** Supabase (Google OAuth + magic link)
- **Auto-deploy:** wtedy GitHub Actions → Hetzner; Vercel na push (API: Render od 2.4)
- **Dokumentacja:** handover, audyt bezpieczeństwa, zaktualizowany README i architektura

### Frontend

- `AuthProvider` — sesja Supabase, timeout ładowania
- `vercel.json` — SPA rewrite + proxy `/api` (fallback)
- `DashboardSummary` — dashboard z raportami, komunikat przy błędzie API
- Env produkcyjne: `VITE_API_URL`, `VITE_SUPABASE_*`

### Backend

- Provisioning użytkownika z Google (`user_metadata.email`)
- Migracja `initial_schema` + moduły rodzinne na Supabase Postgres
- Session pooler Supabase `:5432`

### Infrastruktura

- Fly.io — usunięty z repo (historyczny PoC, nie produkcja)
- Usunięty duplikat `backend/requirements.txt` (Poetry = źródło prawdy)

---

## [2.1] — planowane

- 🧪 Testy — rozszerzenie coverage modułów rodzinnych
- 📊 Eksport Excel — wydatki i budżet do .xlsx
- 📚 Archiwum list — historia odhaczonych zakupów i zadań
- 🔔 Powiadomienia — rozszerzone alerty

---

## [2.0] — 2026-07-26

### Nowe moduły rodzinne

- 🛒 **Lista zakupów** — wspólna checklista per grupa rodzinna
- ✅ **Zadania domowe** — przypisanie, termin
- 🥧 **Budżet miesięczny** — dochody/wydatki, stałe wpisy, live balance
- 📈 **Inwestycje** — lokaty z prognozą zysku
- 👥 **Grupy rodzinne** — zaproszenia, role

### Frontend

- Routing: `/app/shopping`, `/app/tasks`, `/app/budget-monthly`, `/app/investments`, `/app/reports`, `/app/groups`
- Przekierowanie `/app/budget` → `/app/budget-monthly`
- Sidebar, layout mobile

### Backend

- Modele, serwisy, endpointy REST `/api/v1/*`
- Migracje Alembic
- JWT (legacy) / później Supabase w 2.2

---

## [1.0] — 2026-07-26

- UI/UX redesign (zieleń, landing, sidebar mobile)
- Toast, skeletons, login/register
- Routing `/` → landing lub `/app`
