# ==============================================================================
# Gridbricks Trading Dashboard - Frontend Multi-Stage Dockerfile
# Stage 1: Build static assets with Node.js 22 Alpine
# Stage 2: Serve production assets via high-performance Nginx Alpine
# ==============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build static assets
# -----------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Optional build argument for API URL (defaults to empty string for Nginx reverse proxy)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy package manifests first to leverage Docker layer caching
COPY frontend/package.json frontend/package-lock.json* ./

# Install npm dependencies cleanly
RUN npm ci || npm install

# Copy frontend source code
COPY frontend/ ./

# Build production bundle (tsc -b && vite build)
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Production Nginx Server
# -----------------------------------------------------------------------------
FROM nginx:alpine

# Remove default boilerplate website
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with reverse proxy to FastAPI
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose container HTTP port
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
