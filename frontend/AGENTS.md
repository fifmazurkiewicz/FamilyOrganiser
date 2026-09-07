# Frontend

Vite + React SPA. Production: Vercel (`family.fmazurkiewicz.dev`).

## Commands

```bash
npm install
npm run dev
npm run build
```

Leave `VITE_API_URL` empty locally (proxy `/api` → backend :8000). Production: `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (anon only).

Authenticated UI lives under `/app/...`. Taste dials: dashboard overlay in `.cursor/rules/taste-skill-dials.mdc`.
