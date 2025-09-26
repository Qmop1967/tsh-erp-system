# Development Scripts

This directory contains scripts for development environment setup and management.

## Available Scripts

### 🚀 Development Server
- **[dev-start.sh](dev-start.sh)** - Start the development environment
  - Starts FastAPI backend server
  - Starts React frontend development server
  - Configures development database
  - Sets up hot reloading

### 🔍 Status Monitoring
- **[status-check.sh](status-check.sh)** - Check system status and health
  - Monitors database connections
  - Checks API endpoint availability
  - Validates environment configuration
  - Reports system health metrics

## Usage

### Quick Start
```bash
# Start development environment
./scripts/dev/dev-start.sh

# Check system status
./scripts/dev/status-check.sh
```

### Development Workflow
1. **Setup**: Configure environment variables
2. **Start**: Run development servers
3. **Develop**: Make changes with hot reloading
4. **Test**: Run automated tests
5. **Monitor**: Check system status

## Environment Configuration

### Required Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/tsh_erp_dev
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Development Settings
DEBUG=true
ENVIRONMENT=development
```

### Development Database
```bash
# Create development database
createdb tsh_erp_dev

# Run migrations
alembic upgrade head

# Seed development data
python scripts/data/add_demo_data.py
```

## Development Tools

### Code Quality
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **Black**: Python code formatting
- **Flake8**: Python linting

### Testing
- **Jest**: JavaScript unit testing
- **Pytest**: Python unit testing
- **Cypress**: End-to-end testing
- **Flutter Test**: Mobile app testing

### Debugging
- **VS Code**: Integrated debugging
- **Browser DevTools**: Frontend debugging
- **FastAPI Debug**: Backend debugging
- **Flutter Inspector**: Mobile debugging

## Performance Monitoring

### Development Metrics
- **API Response Time**: <100ms for development
- **Database Query Time**: <50ms average
- **Frontend Load Time**: <1s for hot reload
- **Memory Usage**: Monitor for leaks

### Profiling Tools
- **FastAPI Profiler**: API performance profiling
- **React Profiler**: Component performance analysis
- **PostgreSQL Explain**: Query performance analysis
- **Flutter Performance**: Mobile app profiling

## Troubleshooting

### Common Issues
- **Port Conflicts**: Check if ports 8000, 3000 are available
- **Database Connection**: Verify PostgreSQL is running
- **Node Modules**: Run `npm install` if missing dependencies
- **Python Packages**: Run `pip install -r requirements.txt`

### Debug Commands
```bash
# Check running processes
ps aux | grep python
ps aux | grep node

# Check port usage
lsof -i :8000
lsof -i :3000

# Check database connection
psql -h localhost -U username -d tsh_erp_dev

# Check logs
tail -f logs/development.log
```

## Best Practices

### Development Guidelines
- **Code Reviews**: Review all changes before merging
- **Testing**: Write tests for new features
- **Documentation**: Update docs for new functionality
- **Commits**: Use meaningful commit messages

### Performance Tips
- **Database**: Use indexes for frequently queried fields
- **Frontend**: Optimize component re-renders
- **API**: Implement proper caching strategies
- **Mobile**: Optimize image sizes and loading

### Security Notes
- **Environment Variables**: Never commit sensitive data
- **Local Storage**: Use secure storage for tokens
- **HTTPS**: Use HTTPS even in development
- **Input Validation**: Validate all user inputs 