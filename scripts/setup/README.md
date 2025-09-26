# Setup Scripts

This directory contains scripts for initial system setup and configuration.

## Available Scripts

### 🔒 Security Setup
- **[setup-protection.sh](setup-protection.sh)** - System security configuration
  - Firewall configuration
  - SSH hardening
  - SSL certificate setup
  - Security policy enforcement

### 🏗️ Initial Setup Scripts
- **[init_accounting_data.py](init_accounting_data.py)** - Initialize accounting system data
- **[init_cashflow_system.py](init_cashflow_system.py)** - Setup cashflow management
- **[init_items_data.py](init_items_data.py)** - Initialize inventory items

## Usage

### Initial System Setup
```bash
# Complete system setup
./scripts/setup/setup-protection.sh

# Initialize accounting system
python scripts/setup/init_accounting_data.py

# Setup cashflow system
python scripts/setup/init_cashflow_system.py

# Initialize inventory items
python scripts/setup/init_items_data.py
```

### Security Configuration
```bash
# Setup firewall and security
./scripts/setup/setup-protection.sh --security-only

# Configure SSL certificates
./scripts/setup/setup-protection.sh --ssl-only

# Harden SSH configuration
./scripts/setup/setup-protection.sh --ssh-only
```

## Security Features

### Firewall Configuration
- **UFW**: Uncomplicated Firewall setup
- **Port Management**: Open only necessary ports
- **IP Whitelisting**: Restrict access to trusted IPs
- **DDoS Protection**: Rate limiting and connection throttling

### SSH Security
- **Key-based Authentication**: Disable password authentication
- **Port Configuration**: Change default SSH port
- **Fail2Ban**: Automatic IP blocking for failed attempts
- **User Restrictions**: Limit SSH access to specific users

### SSL/TLS Setup
- **Certificate Management**: Let's Encrypt integration
- **HTTPS Enforcement**: Redirect HTTP to HTTPS
- **Security Headers**: HSTS, CSP, and other security headers
- **Cipher Suites**: Strong encryption configuration

## Initial Data Setup

### Accounting System
- **Chart of Accounts**: Standard accounting structure
- **Account Types**: Assets, Liabilities, Equity, Income, Expenses
- **Tax Configurations**: Standard tax rates and rules
- **Currency Setup**: Multi-currency support

### Cashflow System
- **Cash Accounts**: Bank accounts and cash registers
- **Payment Methods**: Credit cards, bank transfers, cash
- **Cashflow Categories**: Income and expense categories
- **Recurring Transactions**: Automated recurring entries

### Inventory System
- **Product Categories**: Hierarchical category structure
- **Unit of Measures**: Standard units (kg, pcs, liters, etc.)
- **Warehouses**: Default warehouse setup
- **Stock Levels**: Initial stock configurations

## Environment Setup

### Development Environment
```bash
# Create development environment
python -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt

# Setup development database
createdb tsh_erp_dev
alembic upgrade head
```

### Production Environment
```bash
# System prerequisites
sudo apt update && sudo apt upgrade -y
sudo apt install postgresql nginx redis-server

# Application setup
./scripts/setup/setup-protection.sh
python scripts/setup/init_accounting_data.py
```

## Configuration Management

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/tsh_erp
REDIS_URL=redis://localhost:6379

# Security Configuration
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# Application Configuration
ENVIRONMENT=production
DEBUG=false
```

### Service Configuration
```bash
# Systemd service setup
sudo cp config/tsh-erp.service /etc/systemd/system/
sudo systemctl enable tsh-erp
sudo systemctl start tsh-erp

# Nginx configuration
sudo cp config/nginx.conf /etc/nginx/sites-available/tsh-erp
sudo ln -s /etc/nginx/sites-available/tsh-erp /etc/nginx/sites-enabled/
```

## System Requirements

### Hardware Requirements
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 100GB+ SSD (500GB+ recommended)
- **Network**: 1Gbps connection for production

### Software Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 8
- **Python**: 3.8 or higher
- **PostgreSQL**: 13 or higher
- **Redis**: 6.0 or higher
- **Nginx**: 1.18 or higher

## Security Checklist

### Pre-Production Security
- [ ] Firewall configuration complete
- [ ] SSH key-based authentication enabled
- [ ] SSL certificates installed and configured
- [ ] Security headers implemented
- [ ] Database access secured
- [ ] Application secrets configured
- [ ] Backup procedures tested
- [ ] Monitoring and alerting setup

### Post-Production Security
- [ ] Regular security updates scheduled
- [ ] Security monitoring enabled
- [ ] Intrusion detection configured
- [ ] Vulnerability scanning automated
- [ ] Access logs monitored
- [ ] Incident response plan documented
- [ ] Security audit completed
- [ ] Compliance requirements met

## Troubleshooting

### Common Setup Issues
- **Permission Errors**: Check file permissions and ownership
- **Database Connection**: Verify PostgreSQL service and credentials
- **Firewall Issues**: Check UFW rules and port access
- **SSL Certificate**: Verify domain configuration and DNS

### Debug Commands
```bash
# Check service status
systemctl status tsh-erp
systemctl status postgresql
systemctl status nginx

# Check logs
tail -f /var/log/tsh-erp/app.log
tail -f /var/log/nginx/error.log
tail -f /var/log/postgresql/postgresql.log

# Test connections
pg_isready -h localhost -U username
redis-cli ping
curl -I https://your-domain.com
```

## Best Practices

### Security Best Practices
- **Principle of Least Privilege**: Grant minimum necessary access
- **Defense in Depth**: Multiple layers of security
- **Regular Updates**: Keep all systems up to date
- **Monitoring**: Continuous security monitoring

### Configuration Management
- **Version Control**: Track configuration changes
- **Environment Separation**: Separate dev/staging/prod configs
- **Secret Management**: Use secure secret storage
- **Documentation**: Document all configuration changes

### Performance Optimization
- **Database Tuning**: Optimize PostgreSQL settings
- **Caching**: Implement Redis caching strategies
- **Load Balancing**: Configure Nginx load balancing
- **Monitoring**: Set up performance monitoring 