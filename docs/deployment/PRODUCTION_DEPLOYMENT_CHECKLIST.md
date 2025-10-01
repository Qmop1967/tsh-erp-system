# 🚀 Production Deployment Checklist

## Pre-Deployment Checklist

### 🔐 Security
- [ ] Update `.env.production` with strong SECRET_KEY
- [ ] Configure production database credentials
- [ ] Set `DEBUG=False` in production
- [ ] Update CORS_ORIGINS with actual production domains
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure secure cookies
- [ ] Review and update all API keys and tokens
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CSP (Content Security Policy) headers

### 🗄️ Database
- [ ] Create production database
- [ ] Run all Alembic migrations
- [ ] Create database backups schedule
- [ ] Configure database connection pooling
- [ ] Set up database monitoring
- [ ] Create read replicas (if needed)
- [ ] Configure automatic backups
- [ ] Test database restore procedure

### 🌐 Backend
- [ ] Install production dependencies
- [ ] Configure production server (Nginx/Apache)
- [ ] Set up process manager (systemd/supervisor)
- [ ] Configure logging
- [ ] Set up error tracking (Sentry/similar)
- [ ] Configure CDN for static files
- [ ] Set up health check endpoints
- [ ] Configure auto-restart on failure

### 💻 Frontend
- [ ] Build optimized production bundle
- [ ] Configure environment variables
- [ ] Set up CDN for assets
- [ ] Enable compression (gzip/brotli)
- [ ] Configure caching headers
- [ ] Optimize images and assets
- [ ] Set up error boundary components
- [ ] Configure analytics

### 📱 Mobile Apps
- [ ] Build release versions for iOS
- [ ] Build release versions for Android
- [ ] Configure API endpoints for production
- [ ] Test on multiple devices
- [ ] Submit to App Store/Play Store
- [ ] Prepare marketing materials
- [ ] Set up push notification service
- [ ] Configure deep linking

### 🔧 Infrastructure
- [ ] Set up production server
- [ ] Configure domain and DNS
- [ ] Set up SSL/TLS certificates (Let's Encrypt)
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up load balancer (if needed)
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation (ELK Stack)
- [ ] Configure backup storage

### 📊 Monitoring & Logging
- [ ] Set up application monitoring
- [ ] Configure error tracking
- [ ] Set up performance monitoring (APM)
- [ ] Configure log rotation
- [ ] Set up alerts for critical errors
- [ ] Configure uptime monitoring
- [ ] Set up database monitoring
- [ ] Create dashboards

### 🧪 Testing
- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Perform load testing
- [ ] Test backup and restore
- [ ] Test failover procedures
- [ ] Security audit
- [ ] Performance testing
- [ ] User acceptance testing

### 📚 Documentation
- [ ] Update API documentation
- [ ] Create deployment documentation
- [ ] Document environment variables
- [ ] Create runbooks for common issues
- [ ] Document backup procedures
- [ ] Create disaster recovery plan
- [ ] Update user documentation
- [ ] Create admin guide

### 🚦 Go-Live
- [ ] Schedule maintenance window
- [ ] Notify users of deployment
- [ ] Create rollback plan
- [ ] Deploy to production
- [ ] Verify all services are running
- [ ] Test critical user flows
- [ ] Monitor logs for errors
- [ ] Update DNS (if needed)
- [ ] Verify SSL certificates
- [ ] Test mobile apps in production

### 📈 Post-Deployment
- [ ] Monitor application performance
- [ ] Check error logs
- [ ] Verify database performance
- [ ] Monitor server resources
- [ ] Collect user feedback
- [ ] Schedule follow-up review
- [ ] Document lessons learned
- [ ] Plan next release

## Environment Variables Template

Copy `.env.production` and update with production values:

```bash
# Backend
DATABASE_URL=postgresql://prod_user:prod_pass@prod_host:5432/erp_db_prod
SECRET_KEY=<generated-strong-key>
DEBUG=False
ENVIRONMENT=production

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_APP_ENV=production

# Mobile
API_BASE_URL=https://api.yourdomain.com
```

## Quick Commands

### Backend Deployment
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r config/requirements.txt

# Run migrations
cd database && alembic upgrade head

# Start with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment
```bash
cd frontend
npm install
npm run build
# Deploy build/ directory to web server
```

### Docker Deployment
```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

## Support Contacts

- **Technical Lead**: [contact info]
- **DevOps**: [contact info]
- **Security**: [contact info]
- **Database Admin**: [contact info]

## Rollback Procedure

If deployment fails:

1. Stop new services
2. Restore from backup
3. Revert database migrations: `alembic downgrade -1`
4. Restart old services
5. Update DNS (if changed)
6. Notify team and users

---

**Last Updated**: September 30, 2025  
**Version**: 1.0.0
