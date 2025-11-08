# Docker Quick Reference Card

## 🚀 Common Commands

### Development

```bash
# Start development environment
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev up -d

# View logs
docker compose logs -f app

# Restart app after code changes
docker compose restart app

# Stop all
docker compose down

# Rebuild app
docker compose build app
docker compose up -d app
```

### Production-like (with Nginx + SSL)

```bash
# Generate SSL cert (dev only)
./scripts/generate_self_signed_cert.sh

# Start with proxy
docker compose --profile proxy up -d

# Check nginx config
docker compose exec nginx nginx -t

# Reload nginx
docker compose exec nginx nginx -s reload
```

### Database Operations

```bash
# Access PostgreSQL
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp

# Run migrations
docker compose exec app alembic upgrade head

# Create backup
./scripts/docker_backup.sh postgres

# Restore backup
./scripts/docker_restore.sh <timestamp> postgres
```

### Redis Operations

```bash
# Access Redis CLI
docker compose exec redis redis-cli

# Check cache stats
docker compose exec redis redis-cli INFO stats

# Flush cache (careful!)
docker compose exec redis redis-cli FLUSHALL

# Create backup
./scripts/docker_backup.sh redis
```

### Monitoring

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Health checks
docker compose exec app curl http://localhost:8000/health

# Logs (last 100 lines)
docker compose logs --tail 100 app

# Follow logs
docker compose logs -f
```

### Backup & Restore

```bash
# Backup everything
./scripts/docker_backup.sh all

# Backup specific service
./scripts/docker_backup.sh postgres
./scripts/docker_backup.sh redis
./scripts/docker_backup.sh uploads

# List backups
./scripts/docker_restore.sh list

# Restore everything
./scripts/docker_restore.sh 20250108_143000 all

# Restore specific service
./scripts/docker_restore.sh 20250108_143000 postgres
```

### Troubleshooting

```bash
# Check configuration
docker compose config

# Validate setup
./scripts/validate_docker_setup.sh

# Inspect container
docker inspect tsh_erp_app

# Enter container shell
docker compose exec app /bin/bash

# View container processes
docker compose exec app ps aux

# Check disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

## 📋 Environment Variables

```bash
# Development
APP_ENV_FILE=.env.dev docker compose up -d

# Staging
APP_ENV_FILE=.env.staging docker compose up -d

# Production
APP_ENV_FILE=.env.production docker compose up -d

# Custom worker count
UVICORN_WORKERS=2 docker compose up -d app

# Custom image version
VERSION=v1.2.3 docker compose build app
```

## 🔧 Profiles

```bash
# Core services only (postgres, redis, app)
docker compose --profile core up -d

# With pgAdmin (development)
docker compose --profile core --profile dev up -d

# With Nginx proxy (production-like)
docker compose --profile proxy up -d

# All services
docker compose --profile core --profile dev --profile proxy up -d
```

## 📁 Important Paths

```
docker-compose.yml           - Main compose file
docker-compose.dev.yml       - Development overrides
Dockerfile                   - Application image
.dockerignore                - Build context exclusions
nginx/nginx.conf             - Nginx configuration
nginx/ssl/                   - SSL certificates
logs/                        - Application logs
uploads/                     - Uploaded files
backups/docker_volumes/      - Docker volume backups
```

## 🔐 SSL Certificates

```bash
# Generate self-signed (dev)
./scripts/generate_self_signed_cert.sh

# Let's Encrypt (production)
# See: docs/docker/SSL_SETUP.md

# Verify certificate
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# Test HTTPS
curl -k https://localhost/health
```

## 📊 Resource Limits

Current limits per service:

| Service | CPU | Memory |
|---------|-----|--------|
| PostgreSQL | 2 cores | 1 GB |
| Redis | 1 core | 512 MB |
| App | 2 cores | 2 GB |
| Nginx | 0.5 cores | 256 MB |

Adjust in `docker-compose.yml` under `deploy.resources.limits`

## 🆘 Emergency Procedures

### App won't start
```bash
docker compose logs app
docker compose build --no-cache app
docker compose up -d app
```

### Database connection failed
```bash
docker compose ps tsh_postgres
docker compose restart tsh_postgres
docker compose logs tsh_postgres
```

### Out of disk space
```bash
docker system df
docker system prune -a
docker volume prune
```

### Restore from backup
```bash
./scripts/docker_restore.sh list
./scripts/docker_restore.sh <timestamp> all
```

## 📞 Getting Help

1. Check logs: `docker compose logs -f`
2. Validate setup: `./scripts/validate_docker_setup.sh`
3. Read docs: `docs/docker/README.md`
4. Full guide: `DOCKER_IMPROVEMENTS_SUMMARY.md`

## 🔗 Useful Links

- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PgAdmin: http://localhost:5050
- Health: http://localhost:8000/health

---

**Pro Tip**: Save this file for quick reference!
