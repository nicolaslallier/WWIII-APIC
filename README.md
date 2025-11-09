# WWIII-APIC

FastAPI backend application following Clean/Hexagonal Architecture with TDD-first approach.

## Architecture

This project follows Clean/Hexagonal Architecture principles:

- **Domain Layer**: Pure business logic, no framework dependencies
- **Use Cases Layer**: Application services that orchestrate domain logic via Protocols
- **Adapters Layer**: Repository implementations and external service adapters
- **API Layer**: FastAPI routers that map HTTP to DTOs
- **Infrastructure Layer**: Database sessions, telemetry, configuration

## Tech Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI (async, OpenAPI-first)
- **Database**: PostgreSQL + SQLAlchemy 2.x + Alembic
- **Testing**: pytest + pytest-asyncio + hypothesis + testcontainers
- **Linting**: ruff + black + mypy (strict)
- **Package Management**: uv
- **Observability**: OpenTelemetry + Prometheus
- **Container**: Docker (multi-stage, non-root)

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- PostgreSQL 16+ (or use Docker Compose)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd WWIII-APIC
```

### 2. Install Dependencies

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
make install
# or
uv pip install -e ".[dev,test]"
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Set DATABASE_URL and any required secrets
```

### 4. Run with Docker Compose

```bash
# Start all services (app, postgres, prometheus)
make docker-up
# or
docker-compose up -d

# Check health
curl http://localhost:8000/healthz
```

### 5. Run Locally (Development)

```bash
# Start PostgreSQL (if not using Docker)
docker-compose up -d postgres

# Run migrations (when Alembic is configured)
# alembic upgrade head

# Run application
uvicorn app.main:app --reload
```

## Development Workflow

### TDD Approach

1. Write failing test first (`tests/unit/`)
2. Implement minimal code to pass
3. Refactor with tests guarding behavior

### Code Quality

```bash
# Format code
make format

# Check formatting
make format-check

# Lint code
make lint

# Type check
make type-check

# Run all quality gates
make quality-gates
```

### Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-integration

# Run e2e tests
make test-e2e

# Run with coverage
make coverage
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
make pre-commit-install

# Run hooks manually
make pre-commit-run
```

## CI/CD

### Custom CI/CD Pipeline

This project uses a homemade CI/CD solution:

```bash
# Run CI pipeline (quality gates + Docker build)
make ci
# or
./scripts/ci.sh

# Run CD pipeline (deployment)
make cd
# or
./scripts/cd.sh

# Run quality gates only
make quality-gates
# or
./scripts/quality-gates.sh
```

### CI Pipeline Steps

1. Linting (ruff)
2. Format check (black)
3. Type checking (mypy)
4. Tests with coverage (pytest)
5. Coverage threshold check (85% minimum)
6. Docker image build
7. Docker healthcheck test

## Project Structure

```
app/
  api/v1/          # FastAPI routers, versioned
  core/            # Core config, settings
  domain/          # Entities, value objects, domain services
  use_cases/       # Application services, Ports (Protocols)
  adapters/        # Repository implementations, external service adapters
  db/              # SQLAlchemy session, engine setup
  models/          # SQLAlchemy ORM models
  schemas/         # Pydantic request/response models
  services/        # Shared services
  infra/
    telemetry/     # OpenTelemetry, logging setup
tests/
  unit/            # Unit tests (70% of tests)
  integration/     # Integration tests (25% of tests)
  e2e/             # End-to-end tests (5% of tests)
scripts/           # CI/CD scripts
```

## Adding a New Endpoint

Follow the TDD workflow:

1. Write unit tests for use_case (`tests/unit/use_cases/test_<feature>.py`)
2. Define Port Protocol (`app/use_cases/ports.py`)
3. Implement use_case (`app/use_cases/<feature>.py`)
4. Write adapter tests (`tests/integration/adapters/test_<feature>_repo.py`)
5. Implement adapter (`app/adapters/repositories/<feature>.py`)
6. Write API tests (`tests/e2e/test_<feature>_api.py`)
7. Implement router + schemas (`app/api/v1/`)
8. Wire in `app/main.py`
9. Add Alembic migration if DB schema changed

## API Endpoints

- `GET /healthz` - Health check
- `GET /readyz` - Readiness check
- `GET /metrics` - Prometheus metrics
- `GET /docs` - Swagger UI (development only)
- `GET /redoc` - ReDoc (development only)
- `GET /api/v1/...` - API endpoints

## Observability

- **Logging**: Structured JSON logs via structlog
- **Metrics**: Prometheus metrics at `/metrics`
- **Tracing**: OpenTelemetry (configure via `OTEL_EXPORTER_OTLP_ENDPOINT`)

## Docker

### Build Image

```bash
make docker-build
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env wwiii-apic:latest
```

### Docker Compose Services

- `app`: FastAPI application
- `postgres`: PostgreSQL database
- `prometheus`: Metrics collection
- `otel-collector`: OpenTelemetry collector (optional)

## Configuration

All configuration is environment-driven via `.env` file. See `.env.example` for available options.

**Important**: Never commit `.env` with real secrets. Use Docker secrets or Key Vaults in production.

## Testing Strategy

- **70% Unit Tests**: Fast, isolated, pure logic
- **25% Integration Tests**: Adapters with real DB (testcontainers)
- **5% E2E Tests**: Full API flows

Coverage threshold: **85% minimum**

## Contributing

1. Follow TDD: Write tests first
2. Apply SOLID principles
3. Keep functions small and readable
4. Use type hints everywhere
5. Run quality gates before committing
6. Use Conventional Commits

## License

MIT

