# Contributing to TSH ERP System

Thank you for your interest in contributing to the TSH ERP System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** - Search the issue tracker to see if the bug has already been reported
2. **Create a detailed bug report** - Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, browser, versions)
   - Screenshots or error logs if applicable

### Suggesting Features

1. **Check existing feature requests** - Look for similar suggestions first
2. **Create a feature request** with:
   - Clear description of the feature
   - Use cases and benefits
   - Proposed implementation (if you have ideas)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** from `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write tests** for new functionality
5. **Ensure all tests pass**
6. **Submit a pull request**

## 🔧 Development Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Flutter 3.0+
- PostgreSQL 12+
- Git

### Local Development

```bash
# Clone your fork
git clone git@github.com:YOUR_USERNAME/tsh-erp-system.git
cd tsh-erp-system

# Set up backend
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt

# Set up frontend
cd frontend
npm install

# Set up database
createdb erp_dev_db
cd ../database
alembic upgrade head
```

## 📝 Code Standards

### Python (Backend)
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **type hints** where appropriate
- Write **docstrings** for functions and classes
- Maximum line length: 100 characters

```bash
# Format code
black app/ tests/

# Check style
flake8 app/ tests/
```

### JavaScript/TypeScript (Frontend)
- Follow **Airbnb style guide**
- Use **Prettier** for formatting
- Use **ESLint** for linting
- Prefer **functional components** with hooks

```bash
# Format and lint
npm run lint
npm run format
```

### Flutter (Mobile)
- Follow **Dart style guide**
- Use **dartfmt** for formatting
- Use **dart analyze** for linting

```bash
# Format code
flutter format .

# Analyze code
flutter analyze
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Mobile Tests
```bash
cd mobile/flutter_apps/admin_dashboard
flutter test
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New features include tests
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive

### Pull Request Template
```
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## 🏗️ Architecture Guidelines

### Backend (FastAPI)
- Use **dependency injection** for database sessions
- Implement **proper error handling**
- Follow **RESTful API** conventions
- Use **Pydantic models** for validation
- Implement **proper logging**

### Frontend (React)
- Use **functional components**
- Implement **proper state management**
- Follow **component composition** patterns
- Use **TypeScript** for type safety
- Implement **proper error boundaries**

### Mobile (Flutter)
- Follow **BLoC pattern** for state management
- Use **proper widget composition**
- Implement **responsive design**
- Handle **platform differences**

## 📚 Documentation

- Update **README.md** for new features
- Add **inline comments** for complex logic
- Update **API documentation** in code
- Add **user guides** for new functionality

## 🔄 Workflow

1. **Issues** - All work should start with an issue
2. **Branches** - Use descriptive branch names
   - `feature/add-inventory-module`
   - `bugfix/fix-login-error`
   - `docs/update-api-docs`
3. **Commits** - Use conventional commit format:
   - `feat: add inventory management module`
   - `fix: resolve login authentication bug`
   - `docs: update API documentation`

## 🎯 Code Review Process

1. **Automatic checks** must pass
2. **At least one reviewer** approval required
3. **Maintainer** final approval for merging
4. **Squash and merge** to keep history clean

## 🚀 Release Process

1. Features merged to `develop` branch
2. Release candidates created from `develop`
3. Testing and bug fixes
4. Merge to `main` for release
5. Tag release with semantic versioning

## ❓ Questions?

- Check the **documentation** first
- Search **existing issues**
- Ask in **discussions** section
- Contact maintainers directly

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to TSH ERP System! 🚀
