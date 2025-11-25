# Simple, robust Dockerfile for Cloud Run
FROM python:3.11-slim

# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements definition
COPY pyproject.toml .

# Install dependencies using standard pip
# We install the package in editable mode or just install deps
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Run using python directly to ensure the __main__ block handles the PORT
CMD ["python", "server.py"]
