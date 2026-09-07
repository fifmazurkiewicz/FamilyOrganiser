# Align hosting docs to Render and bootstrap constitution wiring

**Date:** 2026-09-07  
**Status:** done

## Goal

Record production as Vercel + Render + Supabase (deployment standard) and commit Cursor constitution wiring (Graft, Superpowers, spec-driven, Taste, secrets, language).

## Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-09-07 | Production API is **Render** (Docker Web Service), not Hetzner/Caddy | User confirmed; matches `deployment-standard.mdc` |
| 2026-09-07 | Canonical API hostname stays `api-family.fmazurkiewicz.dev` (Cloudflare CNAME → Render) | Existing product domain + constitution pattern `api-<project>.fmazurkiewicz.dev` |
| 2026-09-07 | Hetzner GitHub Actions deploy is **archived** (`workflow_dispatch` only) | Leftover SSH path must not run on every `main` push |
| 2026-09-07 | Do not invent the Render `*.onrender.com` service name | Not in repo; set in Render dashboard |
| 2026-09-07 | Document ApiPulse as a **known gap** | Required by the standard on Render Free; not in the frontend yet |

## Given / When / Then

- Given docs and `AGENTS.md`, when an agent reads the stack, then they describe Vercel + Render + Supabase (not Hetzner).
- Given `.cursor/rules/`, when a new chat starts in this repo, then Graft, Superpowers, spec-driven, deploy standard, env-secrets, Taste, and language rules are present in git.
- Given local setup, when a developer follows `docs/technical/local-setup.md`, then they can run API + frontend without Docker Desktop.

## Out of scope this session

- Implementing `ApiPulseProvider` / banner
- Adding Alembic to the Docker entrypoint
- Deleting leftover `docker-compose.prod.yml` / Caddy / `scripts/deploy.sh`
