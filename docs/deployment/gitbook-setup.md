# GitBook — podłączenie repozytorium

**Status:** szkielet w repo (`/.gitbook.yaml`, `/docs/SUMMARY.md`)  
**Ostatnia aktualizacja:** 2026-07-30

---

## Co jest gotowe w git

| Plik | Rola |
|------|------|
| `.gitbook.yaml` | root = `docs/`, spis = `SUMMARY.md` |
| `docs/SUMMARY.md` | nawigacja GitBook |
| `docs/**/*.md` | treść (Git Sync) |

---

## Kroki w panelu GitBook (jednorazowo)

1. [app.gitbook.com](https://app.gitbook.com) → **New site** (Ultimate lub Basic).
2. Dodaj space typu **Documentation**.
3. **Integrations → Git Sync** → GitHub → repo `FamilyOrganiser`.
4. Branch: `main`, **Project directory:** `/docs` (monorepo).
5. Sync direction: **Git → GitBook** (edycje w repo, publikacja z GitBook).
6. Po pierwszym syncu: ustaw domenę / branding w ustawieniach site.

Token API (opcjonalnie): [Developer settings](https://app.gitbook.com/account/developer) — tylko poza repo.

---

## Publikacja zmian docs

1. Edytuj pliki w `docs/` na `main`.
2. Git Sync pobierze commit; w GitBook otwórz change request lub merge według polityki site.
3. Po merge CR — **Publish** w GitBook.
