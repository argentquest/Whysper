# Stage 1: Build Frontend
FROM node:18 AS frontend-builder
WORKDIR /app/frontend

# Copy dependency definitions
COPY frontend/package*.json ./
# Install dependencies
RUN npm ci

# Copy source code and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend & Final Image
# Using Red Hat Universal Base Image (UBI) 8 with Python 3.9
FROM registry.access.redhat.com/ubi8/python-39

# Switch to root to install system dependencies
USER root

# Install system libraries required for graphical libraries (like cairosvg)
# and clean up to keep image size down
RUN dnf install -y cairo cairo-gobject pango && dnf clean all

WORKDIR /app

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
# Note: Playwright is installed but browser binaries are skipped to save space.
# If scraping is required, uncomment the next line:
# RUN playwright install chromium --with-deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY backend/ ./backend/

# Copy Frontend Build Artifacts to Static Directory
# The backend is configured to serve files from STATIC_DIR
RUN mkdir -p backend/static
COPY --from=frontend-builder /app/frontend/dist/ ./backend/static/

# Set Environment Variables
ENV PYTHONPATH=/app
ENV STATIC_DIR=/app/backend/static
ENV PORT=8080

# Expose the port (Cloud Run defaults to 8080)
EXPOSE 8080

# Start the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
