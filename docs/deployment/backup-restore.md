# Backup i restore bazy (Supabase Postgres)

**Status:** wdrożone (automatyzacja przez GitHub Actions)  
**Ostatnia aktualizacja:** 2026-07-30

---

## Automatyczny backup

| Element | Wartość |
|---------|---------|
| Workflow | `.github/workflows/backup-supabase.yml` |
| Harmonogram | codziennie o **03:00 UTC** |
| Ręcznie | GitHub → Actions → *Backup Supabase* → *Run workflow* |
| Sekret | `DATABASE_URL` (connection string Supabase, jak przy deploy API) |
| Wynik | artefakt `supabase-backup-<run_id>.sql.gz` (retencja **30 dni**) |

Skrypt: `scripts/backup-supabase.sh` — ten sam dump lokalnie:

```bash
export DATABASE_URL='postgresql://postgres.<ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require'
./scripts/backup-supabase.sh
```

Pliki trafiają do `backups/` (katalog w `.gitignore`).

---

## Restore (dev / staging)

1. Rozpakuj dump: `gunzip -k familyorganiser-YYYYMMDD.sql.gz`
2. Na **pustą** bazę docelową (nie produkcja bez planu):

```bash
psql "$TARGET_DATABASE_URL" -f familyorganiser-YYYYMMDD.sql
```

Dla Supabase: użyj connection stringa z panelu (Session mode, port 5432) i `sslmode=require`.

---

## Uwagi

- Backup obejmuje **schemat + dane aplikacji** w Postgres — nie zastępuje backupów panelu Supabase (PITR na planie płatnym).
- `DATABASE_URL` trzymaj wyłącznie w GitHub Secrets / managerze haseł — nigdy w repo.
- Artefakty GitHub to wygodny fallback; dla długiej retencji rozważ okresowy upload do R2/S3 (poza zakresem v1).
