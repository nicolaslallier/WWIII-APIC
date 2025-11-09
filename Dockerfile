# Multi-stage Dockerfile for WWIII-APIC
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system \
    --no-cache \
    -e ".[dev,test]" && \
    uv pip install --system \
    --no-cache \
    -e .

# Stage 2: Runtime
FROM python:3.12-slim as runtime

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 10001 appuser

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic.ini ./
COPY alembic/ ./alembic/ 2>/dev/null || true

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

