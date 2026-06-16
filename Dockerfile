# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package descriptors first to leverage Docker layer caching
COPY frontend/package*.json ./
RUN npm ci

# Copy the rest of the frontend source
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the FastAPI backend and serve everything
FROM python:3.10-slim

# Install system dependencies including curl for potential health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python requirements first to leverage caching
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend source
COPY backend/ ./backend/

# Copy the compiled static frontend files from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose container port
EXPOSE 3000

# Set default env variables
ENV PORT=3000
ENV DATABASE_URL=sqlite:////var/data/trendcatcher.db

# Run the app from the backend directory using uvicorn, respecting Render's $PORT
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3000}"]
