# ============================================================
# Model Service Dockerfile
#
# WHY slim? python:3.11-slim strips dev tools and saves ~500MB.
# WHY libGL? OpenCV needs it even in headless mode for some ops.
# ============================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps required by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache optimization)
# If requirements.txt hasn't changed, Docker reuses this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Weights are mounted as a volume at runtime (see docker-compose.yml)
# This avoids bloating the image with large binary files
RUN mkdir -p /app/weights /app/logs

EXPOSE 8001

# Health check — used by Docker Compose depends_on
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
