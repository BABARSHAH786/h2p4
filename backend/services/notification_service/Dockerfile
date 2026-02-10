# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy dependency files from backend root
COPY ../../pyproject.toml ../../uv.lock* ./

# Install dependencies using UV
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -m -u 1001 -g appgroup appuser

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy shared backend code (models, database, config)
COPY --chown=appuser:appgroup ../../app/models ./app/models
COPY --chown=appuser:appgroup ../../app/database.py ./app/
COPY --chown=appuser:appgroup ../../app/config.py ./app/
COPY --chown=appuser:appgroup ../../app/__init__.py ./app/

# Copy service-specific code
COPY --chown=appuser:appgroup . ./services/notification_service/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8002

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health/live').read()" || exit 1

# Start application
CMD ["python", "-m", "services.notification_service.main"]
