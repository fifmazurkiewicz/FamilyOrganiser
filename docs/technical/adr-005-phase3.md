# ADR-005: Faza 3 — Testy, API fixes, Excel, Archiwum, Powiadomienia

**Data:** 2026-07-26
**Decyzja:** PM + Lead wspólnie

## Zakres

### 1. Testy (tester + senior-python-developer)
- Testy jednostkowe dla 5 nowych serwisów (shopping, tasks, expenses, budget, investments)
- Testy integracyjne dla 5 nowych routerów API
- Framework: pytest + pytest-asyncio (zgodny z istniejącym stackiem)
- Cel: pokrycie happy path + edge cases

### 2. src/lib/api/* (senior-frontend-developer)
- Utworzenie brakujących plików API dla frontendu:
  - lib/api/auth.ts, lib/api/users.ts, lib/api/transactions.ts
  - lib/api/accounts.ts, lib/api/income.ts, lib/api/investments.ts
  - lib/api/family.ts, lib/api/budgets.ts, lib/api/reports.ts
- Każdy plik: funkcje API korzystające z istniejącego axios clienta

### 3. Excel export (data-engineer + senior-python-developer)
- Endpoint GET /api/v1/expenses/export?year=2026&month=7
- Endpoint GET /api/v1/monthly-budgets/{id}/export
- Format: .xlsx z openpyxl
- Kolumny: data, opis, kwota, typ, kategoria

### 4. Archiwum list (senior-frontend-developer + senior-python-developer)
- Endpoint do pobierania odhaczonych pozycji (shopping + tasks)
- UI: przełącznik "pokaż historię" w każdej liście
- Odfiltrowanie done/bought z domyślnego widoku

### 5. Powiadomienia (senior-ai-developer + senior-python-developer + frontend)
- System powiadomień: "X dodał Y do listy zakupów"
- Model Notification już istnieje — wystarczy stworzyć wpisy przy akcjach
- Frontend: badge z liczbą nieprzeczytanych (już jest), lista powiadomień

## Kolejność
1. lib/api (odblokowuje build)
2. Testy (równolegle)
3. Excel + Archiwum + Powiadomienia (równolegle, zależne od lib/api)