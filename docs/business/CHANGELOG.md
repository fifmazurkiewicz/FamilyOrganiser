# Lista zmian (CHANGELOG)

## [2.0] — 2026-07-26

### Nowe moduły rodzinne

- 🛒 **Lista zakupów** — wspólna checklista per grupa rodzinna, z podglądem kto dodał i kto kupił
- ✅ **Zadania domowe** — lista zadań z przypisaniem do osoby i terminem wykonania
- 🧾 **Wydatki** — prosty dziennik wydatków (kwota + opis + data), sumy miesięczne
- 🥧 **Budżet miesięczny** — dochody i wydatki z flagą "stałe", live balance, kalkulator oszczędności
- 📈 **Inwestycje** — lokaty/obligacje/akcje z auto-obliczaniem daty końca i prognozy zysku

### Backend

- 25 nowych plików: modele SQLAlchemy, schematy Pydantic, serwisy, repozytoria, endpointy REST
- Migracja Alembic dla 8 nowych tabel
- Wszystkie endpointy zabezpieczone JWT

### Frontend

- 10 nowych plików: 5 feature komponentów + 5 stron
- 5 nowych pozycji w sidebarze z ikonami
- Routing: `/app/shopping`, `/app/tasks`, `/app/expenses`, `/app/budget-monthly`, `/app/investments`
- Przekierowanie `/app/budget` → `/app/budget-monthly`

---

## [1.0] — 2026-07-26

### UI/UX Redesign

- Nowa paleta kolorów (ciepła zieleń zamiast niebieskiego)
- Landing page dla niezalogowanych
- Zwijany sidebar na mobile (hamburger)
- Toast notifications
- Loading skeletons
- Login/Register z podziałem na panel brandingu i formularza
- Wskaźnik siły hasła przy rejestracji
- Poprawione komponenty UI (Card, Button, Input, EmptyState)

### Routing

- `/` → Landing page (niezalogowani) / przekierowanie do `/app` (zalogowani)
- `/app` → Dashboard i podstrony