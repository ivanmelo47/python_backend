FROM python:3.13-slim AS base

# Ensure output is flushed immediately and avoid writing pyc files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install build dependencies for optional DB drivers
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libmariadb-dev-compat libmariadb-dev \
	&& rm -rf /var/lib/apt/lists/*

# Create non-root user and set working directory
RUN useradd -m appuser
WORKDIR /app

# Install Python dependencies (copy requirements first for caching)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Fix permissions and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
