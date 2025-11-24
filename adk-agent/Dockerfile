# Production ADK Agent Dockerfile – Cloud Run ready
FROM python:3.11-slim

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

# Copy the entire source tree (including the adk‑agent folder)
COPY . .

# Install Python dependencies (fastapi, uvicorn, google‑adk, etc.)
RUN uv pip install --system -e .



# Expose the port Cloud Run expects
EXPOSE 8080

# Optional health‑check (Cloud Run will call /health)
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the FastAPI app – server.py is in the current directory
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
