FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling packages like psycopg2 if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Set Python path to find app module
ENV PYTHONPATH=/app/backend
ENV PORT=8000

EXPOSE 8000

# Start Uvicorn bound to Render dynamic PORT
CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
