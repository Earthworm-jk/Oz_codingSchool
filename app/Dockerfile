FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Add virtual environment bin directory to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Install uv for fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition files
COPY pyproject.toml uv.lock* ./

# Install dependencies into the virtual environment (.venv)
RUN uv sync --frozen --no-cache

# Copy the rest of the application files
COPY . .

# Expose the application port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
