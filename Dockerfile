# FamilyOrganiser — obraz produkcyjny pod Fly.io (frontend + API, jeden proces).
# Build context: root repozytorium.

# ── Frontend (Vite) ──────────────────────────────────────────────
FROM node:20-alpine AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# Pusty URL = requesty względne /api (ten sam origin co SPA).
ENV VITE_API_URL=
RUN npm run build


# ── Backend deps ─────────────────────────────────────────────────
FROM python:3.12-slim AS backend-build

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.8.4 \
    && poetry config virtualenvs.create false

COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --no-interaction --no-ansi --without dev --no-root


# ── Runtime ──────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /data

COPY --from=backend-build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-build /usr/local/bin /usr/local/bin

COPY backend/app ./app
COPY --from=frontend /frontend/dist ./static
COPY docker/entrypoint-fly.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    STATIC_DIR=/app/static \
    DATABASE_URL=sqlite+aiosqlite:////data/familyorg.db

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8080/api/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
