# Docker Reference

## Overview
- Single FastAPI backend with PostgreSQL, Redis, optional Nginx reverse proxy.
- Compose profiles separate core services (`tsh_postgres`, `tsh_redis`, `tsh_erp_app`) from optional tooling (proxy, pgAdmin).
- Works for local development (`docker-compose.dev.yml`) and production-like deployments (base `docker-compose.yml` with `--profile proxy`).
- Secrets and configuration stay outside the repo; use `.env` files referenced via `APP_ENV_FILE`.
- Background workers run inside the FastAPI container; no separate worker service required today.

## Files
- `docker-compose.yml` – base stack, production defaults, optional profiles.
- `docker-compose.dev.yml` – development overrides (hot reload, bind mounts).
- `Dockerfile` – multi-stage build (builder + runtime) used by `app` service.
- `config/env.example` – baseline application environment variables.
- `config/env.docker.dev.example` – template for `.env.dev` when using Docker locally.
- `deploy.sh` – helper for build/start/stop/status with auto-detected Compose CLI.

## Setup
- Install Docker Engine + Compose plugin (newer Docker Desktop already includes both).
- Copy `config/env.example` → `.env.dev`, then merge overrides from `config/env.docker.dev.example`.
- Ensure `.env.dev` lives in repository root (ignored by git).
- For production, keep `.env.production` outside version control as before.
- Optional: export `COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml` to avoid passing `-f` every time.

## Commands
- `docker compose --profile proxy up -d` → run full stack with Nginx (production style).
- `APP_ENV_FILE=.env.dev docker compose --profile dev -f docker-compose.yml -f docker-compose.dev.yml up` → local dev with auto-reload + pgAdmin.
- `docker compose ps` / `docker compose logs <service>` → inspect status/logs.
- `docker compose run --rm app alembic upgrade head` → run database migrations.
- `docker compose exec tsh_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB` → open psql shell.
- `docker compose down -v` → stop and remove containers + volumes (use cautiously).

## Profiles
- `core` (default) – PostgreSQL, Redis, FastAPI app.
- `proxy` – Nginx reverse proxy (TLS termination, rate limiting).
- `dev` – pgAdmin dashboard; enable with `--profile dev`.
- `cache` – Redis shared profile for clarity; auto-included via `core`.

## Environment Files
- Set `APP_ENV_FILE` to choose which env file the app container loads (`.env.production`, `.env.stage`, `.env.dev`, etc.).
- Optional `POSTGRES_*`, `REDIS_*`, `APP_PORT`, etc. override exposed ports and credentials.
- Keep secrets (API keys, database passwords) out of git; rely on deployment tooling for secure storage.

## Health & Monitoring
- FastAPI exposes `/health`; Compose watch dogs restart container on failure.
- PostgreSQL uses `pg_isready` healthcheck; Redis uses `redis-cli ping`.
- Logs stored on host via bind mounts (`./logs`, `./uploads`); configure external logging if required.

## Testing
- Run unit tests inside container: `docker compose run --rm app pytest`.
- Frontend/mobile tests stay outside Compose (native tooling).
- Use `docker compose exec app python scripts/health_check.sh` for existing health scripts.

## Limitations / Next Steps
- No container for mobile frontends; continue using platform-native tooling.
- SSL certificates for Nginx expected under `nginx/ssl/`.
- Keep parity with non-Docker systemd deployment (documented in `deployment/`); decide per environment which path to use.
- Future enhancements: add Prometheus/Grafana stack via new Compose file, create CI pipeline to build/push Docker images.

