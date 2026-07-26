# API Reference

**Base URL:** `/api/v1`  
**Auth:** Bearer JWT token (header `Authorization: Bearer <token>`)  
**Swagger:** http://localhost:8000/docs (automatycznie generowane przez FastAPI)

---

## 🛒 Shopping Lists

### Lista list zakupowych
```
GET /api/v1/shopping/lists?family_group_id=<uuid>
Response: [{ id, name, created_by, created_at, items: [...] }]
```

### Utwórz listę
```
POST /api/v1/shopping/lists
Body: { name: "Zakupy na weekend", family_group_id: "<uuid>" }
Response: { id, name, created_by, created_at, items: [] }
```

### Pobierz pozycje listy
```
GET /api/v1/shopping/lists/{list_id}/items
Response: [{ id, name, quantity, added_by, bought_by, bought_at, is_bought }]
```

### Dodaj pozycję
```
POST /api/v1/shopping/lists/{list_id}/items
Body: { name: "Chleb", quantity: 2 }
Response: { id, name, quantity, is_bought: false, ... }
```

### Przełącz status kupienia
```
PATCH /api/v1/shopping/items/{item_id}/toggle
Response: { id, is_bought: true, bought_by: "<user_id>", bought_at: "2026-..." }
```

---

## ✅ Tasks

### Lista list zadań
```
GET /api/v1/tasks/lists?family_group_id=<uuid>
```

### Utwórz listę
```
POST /api/v1/tasks/lists
Body: { name: "Dom", family_group_id: "<uuid>" }
```

### Dodaj zadanie
```
POST /api/v1/tasks/lists/{list_id}/items
Body: { title: "Odkurzyć salon", assigned_to: "<user_id>?", due_date: "2026-..." }
```

### Przełącz status wykonania
```
PATCH /api/v1/tasks/items/{item_id}/toggle
Response: { is_done: true, done_by: "<user_id>", done_at: "2026-..." }
```

---

## 🧾 Simple Expenses

### Lista wydatków
```
GET /api/v1/simple-expenses?family_group_id=<uuid>&year=2026&month=7
Response: [{ id, amount, description, expense_date, user_id, created_at }]
```

### Dodaj wydatek
```
POST /api/v1/simple-expenses
Body: { amount: 49.99, description: "Buty dla dziecka", expense_date: "2026-07-26" }
```

### Usuń wydatek (tylko właściciel)
```
DELETE /api/v1/simple-expenses/{expense_id}
```

---

## 🥧 Monthly Budget

### Pobierz lub utwórz budżet na miesiąc
```
GET /api/v1/monthly-budgets?family_group_id=<uuid>&year=2026&month=7
Response: { id, year, month, entries: [...], summary: { total_income, total_expenses, remaining } }
```

### Dodaj wpis
```
POST /api/v1/monthly-budgets/{budget_id}/entries
Body: { type: "income"|"expense", name: "Pensja", amount: 5000, is_recurring: false }
```

### Usuń wpis
```
DELETE /api/v1/monthly-budgets/{budget_id}/entries/{entry_id}
```

---

## 📈 Simple Investments

### Lista inwestycji
```
GET /api/v1/simple-investments?family_group_id=<uuid>
Response: [{ id, name, investment_type, principal_amount, interest_rate, ...,
             end_date, projected_profit, projected_total }]
```

### Podsumowanie
```
GET /api/v1/simple-investments/summary?family_group_id=<uuid>
Response: { total_principal, total_projected_profit, total_projected_value }
```

### Dodaj inwestycję
```
POST /api/v1/simple-investments
Body: {
  name: "Lokata 6m PKO",
  investment_type: "deposit",
  principal_amount: 10000,
  interest_rate: 5.5,
  interest_period: "yearly",
  start_date: "2026-07-26",
  duration_value: 6,
  duration_unit: "months"
}
Response: { ..., end_date: "2027-01-26", projected_profit: 275.00, projected_total: 10275.00 }
```

### Usuń
```
DELETE /api/v1/simple-investments/{investment_id}
```