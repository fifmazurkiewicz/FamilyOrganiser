# ADR-006: User approval gate

**Date:** 2026-09-07  
**Status:** Accepted

## Decision

Public signup stays. New app users are created with `users.is_approved = false` unless their email is on the admin allowlist (`ADMIN_EMAIL` or the bootstrap owner `fifmazurkiewicz@gmail.com`). Allowlist emails are promoted to `is_approved` + `is_app_admin` on **every login**, so a first signup that landed on the waiting screen is unblocked after env/code is corrected. Existing non-allowlist rows stay as grandfathered by the migration (`UPDATE ... SET is_approved = true`). There is no LLM spend quota in this app; the gate is access-only.

Unapproved users may authenticate. `GET /api/v1/users/me` stays available (and returns `is_approved`) so the client can poll. All other authenticated feature APIs use `require_approved` and return **403** with `detail: "account_pending_approval"`.

`get_current_user` does **not** check approval. It still 403s only for `is_active` / `is_locked`. Approval is a separate flag.

App-admins toggle access with `POST /users/{id}/approve` and `POST /users/{id}/revoke`. An admin cannot revoke themselves. No notifications are sent.

The SPA shows a single waiting screen (no `/app/*` chrome) until `is_approved` is true. Revoke returns the user to that screen.

## Why

Family Organiser is a private family app. Open Supabase signup is convenient, but product modules must stay closed until an existing admin accepts the account. Reusing `is_active` / `is_locked` would mix lockout with onboarding and break `/users/me`.

## Consequences

- Alembic `add_user_is_approved`: add column, grandfather existing users, default new rows to `false`.
- Frontend: waiting screen polls `/v1/users/me` every 15s; admin list shows Oczekuje / Zaakceptowany.
