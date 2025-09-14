# Multi-stage build for Full-Stack deployment
FROM node:18-alpine AS frontend-build

# Build frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock* ./
RUN yarn install --frozen-lockfile
COPY frontend/ ./
RUN yarn build

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/build ./static/

# Create uploads directory for any file uploads
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8001

# Start command
CMD ["python", "backend/server.py"]