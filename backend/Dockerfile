# Use a Python image with uv installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev -o requirements.txt

# Final stage
FROM python:3.12-slim-bookworm

WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

# Set environment variables
ENV PYTHONPATH="/app"

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
