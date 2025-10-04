#!/usr/bin/env python3
"""
Advanced Security Integration Script
Integrates all security components into the main application
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def integrate_security_routes():
    """Integrate security routes into main application"""
    print("🔗 Integrating security routes...")
    
    main_app_file = project_root / "app" / "main.py"
    
    if not main_app_file.exists():
        print("❌ Main app file not found")
        return False
    
    # Read current main.py
    with open(main_app_file, 'r') as f:
        content = f.read()
    
    # Add security router imports if not present
    security_imports = """
from app.routers.advanced_security import router as advanced_security_router
from app.routers.security_admin import router as security_admin_router
"""
    
    # Add router includes if not present
    router_includes = """
# Advanced Security Routes
app.include_router(advanced_security_router, prefix="/api/v1")
app.include_router(security_admin_router, prefix="/api/v1")
"""
    
    if "advanced_security_router" not in content:
        # Find import section
        if "from app.routers" in content:
            content = content.replace(
                "from app.routers", 
                security_imports + "\nfrom app.routers"
            )
        else:
            # Add imports after fastapi import
            content = content.replace(
                "from fastapi import FastAPI",
                "from fastapi import FastAPI" + security_imports
            )
        
        # Add router includes
        if "app = FastAPI(" in content:
            # Find the end of FastAPI app creation
            app_creation_end = content.find("app = FastAPI(")
            if app_creation_end != -1:
                # Find the next line after app creation
                next_line = content.find("\n", app_creation_end + 100)
                if next_line != -1:
                    content = content[:next_line] + router_includes + content[next_line:]
        
        # Write back to file
        with open(main_app_file, 'w') as f:
            f.write(content)
        
        print("✅ Security routes integrated")
    else:
        print("✅ Security routes already integrated")
    
    return True

def update_requirements():
    """Update requirements.txt with security dependencies"""
    print("📦 Updating requirements...")
    
    requirements_file = project_root / "requirements.txt"
    
    security_deps = [
        "cryptography>=41.0.0",
        "pyotp>=2.9.0",
        "qrcode[pil]>=7.4.2",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "firebase-admin>=6.2.0",
        "twilio>=8.5.0",
        "geoip2>=4.7.0",
        "user-agents>=2.2.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.1",
        "python-magic>=0.4.27",
        "pillow>=10.0.0",
        "openpyxl>=3.1.2",
        "pandas>=2.1.0",
        "numpy>=1.25.0",
        "scikit-learn>=1.3.0",
        "redis>=4.6.0",
        "celery>=5.3.0",
    ]
    
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            current_reqs = f.read()
        
        new_deps = []
        for dep in security_deps:
            pkg_name = dep.split('>=')[0].split('[')[0]
            if pkg_name not in current_reqs:
                new_deps.append(dep)
        
        if new_deps:
            with open(requirements_file, 'a') as f:
                f.write('\n# Advanced Security Dependencies\n')
                for dep in new_deps:
                    f.write(f"{dep}\n")
            print(f"✅ Added {len(new_deps)} new security dependencies")
        else:
            print("✅ Security dependencies already present")
    else:
        with open(requirements_file, 'w') as f:
            f.write("# TSH ERP System Requirements\n\n")
            f.write("# Core Dependencies\n")
            f.write("fastapi>=0.104.0\n")
            f.write("uvicorn[standard]>=0.24.0\n")
            f.write("sqlalchemy>=2.0.0\n")
            f.write("psycopg2-binary>=2.9.0\n")
            f.write("alembic>=1.12.0\n")
            f.write("pydantic>=2.4.0\n")
            f.write("python-dotenv>=1.0.0\n")
            f.write("\n# Advanced Security Dependencies\n")
            for dep in security_deps:
                f.write(f"{dep}\n")
        print("✅ Created requirements.txt with security dependencies")

def create_docker_security_config():
    """Create Docker configuration for security services"""
    print("🐳 Creating Docker security configuration...")
    
    docker_dir = project_root / "docker"
    docker_dir.mkdir(exist_ok=True)
    
    security_compose = docker_dir / "docker-compose.security.yml"
    
    compose_content = """version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    networks:
      - tsh_security_network

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    environment:
      - POSTGRES_DB=${DATABASE_NAME}
      - POSTGRES_USER=${DATABASE_USER}
      - POSTGRES_PASSWORD=${DATABASE_PASSWORD}
    networks:
      - tsh_security_network

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - tsh_security_network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - tsh_security_network

  tsh_erp_app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://redis:6379/0
      - SECURITY_ENCRYPTION_KEY=${SECURITY_ENCRYPTION_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ../app:/app/app
      - ../logs:/app/logs
    networks:
      - tsh_security_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ../ssl:/etc/nginx/ssl
    depends_on:
      - tsh_erp_app
    networks:
      - tsh_security_network

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:

networks:
  tsh_security_network:
    driver: bridge
"""
    
    with open(security_compose, 'w') as f:
        f.write(compose_content)
    
    print("✅ Docker security configuration created")

def create_nginx_config():
    """Create Nginx configuration for security"""
    print("🌐 Creating Nginx security configuration...")
    
    docker_dir = project_root / "docker"
    nginx_config = docker_dir / "nginx.conf"
    
    nginx_content = """events {
    worker_connections 1024;
}

http {
    upstream tsh_erp_backend {
        server tsh_erp_app:8000;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://tsh_erp_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login endpoint with stricter limits
        location /api/v1/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://tsh_erp_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://tsh_erp_backend;
            access_log off;
        }
    }
}
"""
    
    with open(nginx_config, 'w') as f:
        f.write(nginx_content)
    
    print("✅ Nginx security configuration created")

def create_systemd_service():
    """Create systemd service for the application"""
    print("🔧 Creating systemd service...")
    
    service_content = """[Unit]
Description=TSH ERP System with Advanced Security
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=tsh-erp
Group=tsh-erp
WorkingDirectory=/opt/tsh-erp
Environment=PATH=/opt/tsh-erp/venv/bin
ExecStart=/opt/tsh-erp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tsh-erp

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/tsh-erp/logs /opt/tsh-erp/temp

[Install]
WantedBy=multi-user.target
"""
    
    systemd_dir = project_root / "scripts" / "systemd"
    systemd_dir.mkdir(exist_ok=True)
    
    service_file = systemd_dir / "tsh-erp.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created")
    print(f"   Location: {service_file}")
    print("   To install: sudo cp scripts/systemd/tsh-erp.service /etc/systemd/system/")

def create_backup_script():
    """Create automated backup script"""
    print("💾 Creating backup script...")
    
    backup_script = project_root / "scripts" / "backup" / "automated_backup.sh"
    backup_script.parent.mkdir(exist_ok=True)
    
    script_content = """#!/bin/bash
# TSH ERP System - Automated Backup Script

set -e

# Configuration
BACKUP_DIR="/opt/backups/tsh-erp"
DATABASE_NAME="tsh_erp_db"
DATABASE_USER="postgres"
RETENTION_DAYS=30
ENCRYPTION_KEY_FILE="/opt/tsh-erp/config/backup.key"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/tsh_erp_backup_$TIMESTAMP"

echo "Starting backup at $(date)"

# Database backup
echo "Backing up database..."
pg_dump -U "$DATABASE_USER" -h localhost "$DATABASE_NAME" > "$BACKUP_FILE.sql"

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_FILE.sql"

# Encrypt backup
if [ -f "$ENCRYPTION_KEY_FILE" ]; then
    echo "Encrypting backup..."
    openssl enc -aes-256-cbc -salt -in "$BACKUP_FILE.sql.gz" -out "$BACKUP_FILE.sql.gz.enc" -pass file:"$ENCRYPTION_KEY_FILE"
    rm "$BACKUP_FILE.sql.gz"
    FINAL_BACKUP="$BACKUP_FILE.sql.gz.enc"
else
    echo "Warning: Encryption key not found, backup not encrypted"
    FINAL_BACKUP="$BACKUP_FILE.sql.gz"
fi

# File system backup (configurations, logs)
echo "Backing up configuration files..."
tar -czf "$BACKUP_FILE.config.tar.gz" /opt/tsh-erp/config /opt/tsh-erp/logs

# Clean old backups
echo "Cleaning old backups..."
find "$BACKUP_DIR" -name "tsh_erp_backup_*" -mtime +$RETENTION_DAYS -delete

# Verify backup
echo "Verifying backup..."
if [ -f "$FINAL_BACKUP" ] && [ -s "$FINAL_BACKUP" ]; then
    echo "Backup completed successfully: $FINAL_BACKUP"
    echo "Backup size: $(du -h "$FINAL_BACKUP" | cut -f1)"
    
    # Log to syslog
    logger "TSH ERP backup completed: $FINAL_BACKUP"
else
    echo "Backup failed!"
    logger -p err "TSH ERP backup failed"
    exit 1
fi

echo "Backup completed at $(date)"
"""
    
    with open(backup_script, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(backup_script, 0o755)
    
    print("✅ Backup script created")
    print(f"   Location: {backup_script}")
    print("   To schedule: Add to crontab: 0 2 * * * /path/to/automated_backup.sh")

def create_monitoring_config():
    """Create monitoring configuration"""
    print("📊 Creating monitoring configuration...")
    
    monitoring_dir = project_root / "monitoring"
    monitoring_dir.mkdir(exist_ok=True)
    
    # Prometheus configuration
    prometheus_config = monitoring_dir / "prometheus.yml"
    with open(prometheus_config, 'w') as f:
        f.write("""global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "security_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'tsh-erp'
    static_configs:
      - targets: ['tsh_erp_app:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
""")
    
    # Security alerting rules
    security_rules = monitoring_dir / "security_rules.yml"
    with open(security_rules, 'w') as f:
        f.write("""groups:
- name: security_alerts
  rules:
  - alert: HighFailedLoginRate
    expr: rate(failed_logins_total[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: High failed login rate detected
      description: "Failed login rate is {{ $value }} per second"

  - alert: SuspiciousActivity
    expr: high_risk_sessions_total > 5
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: Suspicious activity detected
      description: "{{ $value }} high-risk sessions detected"

  - alert: SecurityPolicyViolation
    expr: rate(policy_violations_total[1m]) > 0
    for: 0s
    labels:
      severity: warning
    annotations:
      summary: Security policy violation
      description: "Policy violation rate: {{ $value }} per second"
""")
    
    print("✅ Monitoring configuration created")

def main():
    """Main integration function"""
    print("🚀 TSH ERP Advanced Security Integration")
    print("=" * 50)
    
    success = True
    
    try:
        # Integrate routes
        if not integrate_security_routes():
            success = False
        
        # Update requirements
        update_requirements()
        
        # Create Docker configuration
        create_docker_security_config()
        create_nginx_config()
        
        # Create system services
        create_systemd_service()
        create_backup_script()
        
        # Create monitoring
        create_monitoring_config()
        
        if success:
            print("\n🎉 Advanced Security Integration Complete!")
            print("=" * 50)
            print("\n📋 Next Steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Configure environment: cp .env.example .env")
            print("3. Run migrations: python scripts/migrations/create_advanced_security_system.py")
            print("4. Start services: docker-compose -f docker/docker-compose.security.yml up -d")
            print("5. Test mobile app: cd mobile/flutter_apps/09_tsh_mfa_authenticator && flutter run")
            print("6. Access security admin: http://localhost:8000/api/v1/admin/security/dashboard")
            
            print("\n🔒 Security Features Integrated:")
            print("• Multi-layered access control (ABAC, RBAC, PBAC)")
            print("• Row-Level Security (RLS) and Field-Level Security (FLS)")
            print("• Mobile MFA application with biometric authentication")
            print("• Comprehensive audit logging and monitoring")
            print("• Real-time threat detection and response")
            print("• Automated backup and recovery")
            print("• Compliance reporting (GDPR, CCPA, SOX, ISO27001)")
            
            print("\n📱 Mobile App Features:")
            print("• Real-time MFA approval notifications")
            print("• Biometric authentication (fingerprint, face, voice)")
            print("• Device and session management")
            print("• Location-based access control")
            print("• Risk assessment dashboard")
            print("• Emergency lockdown capabilities")
            
            print("\n🛡️ Security Policies Active:")
            print("• Business hours access restrictions")
            print("• Geographic access limitations")
            print("• High-risk action MFA requirements")
            print("• Automated threat response")
            print("• Data privacy and protection")
            
        else:
            print("\n⚠️ Integration completed with warnings")
            print("Please review the output above for any issues")
    
    except Exception as e:
        print(f"\n❌ Integration failed: {e}")
        return False
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
