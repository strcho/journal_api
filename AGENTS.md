# Repository Guidelines for Agentic Coding

## Project Overview
This is a FastAPI-based journal synchronization service with MongoDB and Redis persistence. The API supports user authentication, journal entry synchronization, attachment management, and Qiniu cloud storage integration.

 ## Build, Test, and Development Commands

 - **Environment Setup**:
   - `pipenv install --dev` installs all dependencies including dev tools
   - `pipenv shell` activates the virtual environment (preferred over `pipenv run`)
   - `pipenv --venv` shows the virtual environment path
   - `pipenv --rm` removes and recreates the virtual environment

 - **Dependency Management**:
   - Add production dependencies: `pipenv install package_name`
   - Add dev dependencies: `pipenv install --dev package_name`
   - Remove dependencies: `pipenv uninstall package_name`
   - Update lock file: `pipenv lock` (run after dependency changes)
   - Sync environment: `pipenv sync` (installs exact versions from Pipfile.lock)
   - Check security: `pipenv check`
   - View dependency tree: `pipenv graph`

 - **Development Workflow**:
   - Run app locally: `pipenv run dev` (uses predefined script)
   - Quick endpoint check: `pipenv run curl http://127.0.0.1:8000/hello/YourName` or use requests in `test_main.http`
   - Run tests: `pipenv run test --maxfail=1 -q` for faster feedback
   - Code formatting: `pipenv run format` (runs black on all files)
   - Linting: `pipenv run lint` (runs flake8 for code quality)
   - Security check: `pipenv run check` (scans for known vulnerabilities)

 - **Pipenv Best Practices**:
   - Always commit `Pipfile.lock` to ensure reproducible environments
   - Use `--dev` flag for development-only dependencies (pytest, black, flake8, etc.)
   - Run `pipenv lock` after modifying Pipfile to update lock file
   - Use `pipenv install --deploy` in CI/CD to ensure exact versions
   - Avoid editing Pipfile.lock manually; let pipenv manage it
   - Use specific versions for critical dependencies (`package = "1.2.3"`)
   - Use flexible versions for less critical dependencies (`package = "*"`)
   - Configure custom sources (like aliyun mirror) for faster installations
   - Run `pipenv check` regularly to identify security vulnerabilities

 ### Environment Setup
```bash
# Install dependencies
pipenv install --dev

# Enter virtual environment
pipenv shell

# Clean Python cache and build artifacts
make clean
```

### Development Server
```bash
# Start development server with hot reload
pipenv run uvicorn app.main_v2:app --reload --host 0.0.0.0 --port 8000

# Or use Makefile
make dev
```

### Testing Commands
```bash
# Run all tests
pipenv run pytest -v
make test

# Run single test file
pipenv run pytest tests/test_auth.py -v

# Run specific test function
pipenv run pytest tests/test_auth.py::test_login_success -v

# Run with coverage
pipenv run pytest --cov=app --cov-report=html

# Stop on first failure for faster feedback
pipenv run pytest --maxfail=1 -q
```

### Docker Commands
```bash
# Start development environment
docker-compose up -d
make docker-up

# Start production environment
docker-compose -f docker-compose.prod.yml up -d
make docker-prod-up

# View logs
docker-compose logs -f api
make docker-logs

# Stop services
docker-compose down
make docker-down
```

## Project Structure & Module Organization
- `main.py` - Legacy uvicorn entrypoint (use `app.main_v2` for current development)
- `app/main_v2.py` - Current FastAPI app entrypoint with MongoDB/Redis integration
- `app/main.py` - Legacy in-memory store version
- `app/api/routes/` - FastAPI routers organized by feature:
  - `auth_v2.py` - Authentication endpoints (login, refresh, validation)
  - `sync_v2.py` - Journal synchronization endpoints
  - `attachments_v2.py` - Attachment upload/download endpoints
  - `storage_v2.py` - Cloud storage token endpoints
  - `health.py` - Health check endpoints
- `app/services/` - Business logic layer separated from HTTP concerns:
  - `auth_v2.py` - Authentication service with token management
  - `sync_v2.py` - Journal synchronization logic
  - `attachments_v2.py` - Attachment processing and storage
  - `qiniu.py` - Qiniu cloud storage integration
- `app/database/` - Data persistence layer:
  - `mongo.py` - MongoDB connection and models
  - `redis.py` - Redis cache integration
- `app/schemas/` - Pydantic models for request/response validation
- `app/core/` - Shared utilities and error handling
- `Pipfile` - Python 3.11 with specific FastAPI, MongoDB, Redis, and Qiniu dependencies

## Code Style & Naming Conventions

### Python Style
- **Python Version**: 3.11 (as specified in Pipfile)
- **Formatting**: PEP 8 compliant (4-space indents, snake_case functions/variables, CapWords classes)
- **Type Hints**: Required on all function signatures and public APIs
- **Line Length**: Maximum 88 characters (Black default)

### Import Organization
```python
# Standard library imports
import uuid
from datetime import datetime
from typing import Optional

# Third-party imports
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

# Local imports
from app.api.deps_v2 import get_mongo_store_dep
from app.schemas.auth import LoginRequest
from app.services.auth_v2 import AuthService
```

### Naming Patterns
- **Files**: `snake_case.py` (e.g., `auth_service.py`, `sync_v2.py`)
- **Classes**: `CapWords` (e.g., `AuthService`, `MongoRefreshToken`)
- **Functions/Variables**: `snake_case` (e.g., `login_user`, `access_token`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_EXPIRE_TIME`)
- **Endpoints**: kebab-case URLs (e.g., `/auth/login`, `/sync/changes`)

### Error Handling Patterns
- Use the centralized `http_error()` function from `app.core.errors`
- Standardized error response format with `ErrorResponse` and `ErrorDetail`
- Include specific error codes and messages for API consumers
- Use appropriate HTTP status codes (401 for auth, 403 for forbidden, 422 for validation)

### Service Layer Architecture
- **Routes**: Handle HTTP concerns only (request/response, status codes, dependencies)
- **Services**: Contain business logic, database operations, and external service calls
- **Schemas**: Define data contracts with Pydantic models
- **Dependency Injection**: Use FastAPI's `Depends()` for clean separation of concerns

### Database Patterns
- **MongoDB**: Use Motor async driver with Pydantic models for structure
- **Redis**: Use hiredis for performance, set appropriate expiration times
- **Caching**: Cache frequently accessed data (auth tokens, user sessions)
- **Connection Management**: Use dependency injection for connection lifecycle

### API Design Guidelines
- **Async/Await**: All route handlers and service methods must be async
- **Response Models**: Always specify `response_model` in route decorators
- **Error Responses**: Define error responses in route decorators for OpenAPI documentation
- **Versioning**: Use `v2` suffix for current API versions (e.g., `auth_v2.py`)

### Security Best Practices
- Token-based authentication with access/refresh token pattern
- Store refresh tokens in MongoDB, access tokens in Redis with TTL
- UUID-based tokens for uniqueness and security
- Device-based token isolation for multi-device support

### Testing Guidelines
- **Test Structure**: Mirror application structure in `tests/` directory
- **Test Naming**: `test_*.py` files, `test_*()` functions
- **Test Coverage**: Target routes, services, and critical business logic
- **Manual Testing**: Update `test_main.http` with example requests for new endpoints
- **Test Types**: Include unit tests for services, integration tests for routes
- **Fixtures**: Use pytest fixtures for database setup and teardown

### Environment Configuration
- Use `.env` file for local development (copy from `.env.example`)
- Required environment variables: MongoDB URL, Redis URL, Qiniu credentials
- Docker Compose includes MongoDB and Redis services for development
- Production uses separate `docker-compose.prod.yml` configuration

### Commit & Code Review Guidelines
- **Commits**: Short, imperative subjects (e.g., "Add user authentication endpoint")
- **PR Descriptions**: Include intent, key changes, and verification steps
- **Breaking Changes**: Clearly document any API changes or new required environment variables
- **Code Quality**: Ensure all type hints pass and no unused imports remain

## 沟通与输出
- 与开发者交流时使用中文
- 回复时给出简洁的小结，便于快速了解修改内容
- 重要修改需要说明影响范围和测试方法
