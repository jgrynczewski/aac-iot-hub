 # Multi-stage build for smaller final image

# Stage 1: Builder - install dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - copy only what's needed
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security (before copying files)
RUN useradd -m -u 1000 aac

# Copy installed packages from builder to user's home directory
COPY --from=builder /root/.local /home/aac/.local

# Copy application code
COPY ./app ./app

# Set ownership
RUN chown -R aac:aac /app /home/aac/.local

USER aac

# Add .local/bin to PATH (for uvicorn executable)
ENV PATH=/home/aac/.local/bin:$PATH

# Expose port (documentation only - host mode ignores this)
EXPOSE 8765

# Health check - verify API is responding
# Checks /api/health endpoint every 30s
# Waits 5s before first check (startup time)
# Retries 3 times before marking unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/api/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765", "--log-level", "info"]