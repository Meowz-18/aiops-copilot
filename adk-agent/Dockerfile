# Production ADK Agent Dockerfile – Cloud Run ready
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies (curl for health‑check)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to the repository root inside the container
WORKDIR /app

# Copy only the pyproject.toml for caching
COPY pyproject.toml ./

# Install UV (fast installer) for Python dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1

# Copy the entire source tree
COPY . .

# Install Python dependencies (non-editable for production)
# We use --no-cache-dir to keep the image small and ensure fresh installs
RUN uv pip install --system --no-cache-dir .

# Expose the port Cloud Run expects
EXPOSE 8080

# Run the FastAPI app using uvicorn, listening on the PORT environment variable
# We use sh -c to expand the PORT variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
