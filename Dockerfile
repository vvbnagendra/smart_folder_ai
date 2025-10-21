# --- Stage 1: Build the React Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build


# --- Stage 2: Build the Python Backend and Final Image ---
FROM python:3.11-slim AS final-builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# --- ✅ Install system dependencies for dlib, OpenCV, and face-recognition ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk2.0-dev \
    libboost-all-dev \
    pkg-config \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    zlib1g-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Upgrade pip ---
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# --- Try installing prebuilt dlib binary first ---
RUN pip install --no-cache-dir --prefer-binary dlib==19.24.2 || true

# --- Install remaining Python dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy backend code ---
COPY app/ app/
COPY sample.env .

# --- Copy built frontend static files into backend's static directory ---
COPY --from=frontend-builder /app/frontend/dist /app/app/static

# --- Create directories and set permissions ---
RUN mkdir -p /data /app/logs && chown -R app:app /app /data

# --- Switch to non-root user ---
USER app

# --- Expose port ---
EXPOSE 8080

# --- Health check ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/status || exit 1

# --- Entrypoint ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
