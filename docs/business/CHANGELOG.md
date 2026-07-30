# Lista zmian (CHANGELOG)

## [2.2] — 2026-07-30 — Produkcja

### 🚀 Wdrożenie produkcyjne

- **Frontend live:** [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev) (Vercel)
- **API live:** [api-family.fmazurkiewicz.dev](https://api-family.fmazurkiewicz.dev) (Hetzner + Caddy)
- **Auth:** Supabase (Google OAuth + magic link)
- **Auto-deploy:** GitHub Actions → Hetzner; Vercel na push
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

- Fly.io przeniesiony do `archive/fly/` (nie produkcja)
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
