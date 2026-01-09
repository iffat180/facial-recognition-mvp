#!/bin/bash
# Railway startup script - uses PORT environment variable

# Set default port if PORT is not set
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
