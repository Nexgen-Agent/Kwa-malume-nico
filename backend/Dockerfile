# Stage 1: Builder
# This stage installs all Python and system dependencies
FROM python:3.13-slim-bookworm as builder

# Set environment variables for a clean build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system build dependencies and curl for health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory for the application
WORKDIR /app

# Copy requirements and install them into a virtual environment
COPY requirements.txt .
RUN python -m venv /venv
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Production Image
# This stage is for the final, lightweight runtime image
FROM python:3.13-slim-bookworm

# Install only the necessary runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app

# Copy the virtual environment and application code from the builder stage
COPY --from=builder /venv /venv
COPY app ./app
COPY seeder.py .

# Copy and make the entrypoint script executable
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Add the virtual environment to the PATH
ENV PATH="/venv/bin:$PATH"

EXPOSE 4000

# Health check to ensure container is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:4000/health || exit 1

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]