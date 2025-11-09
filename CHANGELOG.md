# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added

- Initial project setup with Clean/Hexagonal Architecture
- FastAPI application with health/readiness endpoints
- PostgreSQL database integration with SQLAlchemy 2.x async
- Docker multi-stage build with non-root user
- Docker Compose setup with PostgreSQL and Prometheus
- Testing infrastructure (pytest, testcontainers, hypothesis)
- Code quality tools (ruff, black, mypy) with strict configuration
- Pre-commit hooks for code quality
- Custom CI/CD pipeline (Makefile + shell scripts)
- Structured JSON logging with structlog
- Prometheus metrics endpoint
- OpenTelemetry integration (configured, ready for use)
- Comprehensive project documentation

### Infrastructure

- Project structure following Clean Architecture layers
- Dependency management with `uv`
- Environment-based configuration with Pydantic Settings
- Coverage reporting with 85% threshold
- EditorConfig for consistent formatting

[0.1.0]: https://github.com/yourorg/wwiii-apic/releases/tag/v0.1.0

