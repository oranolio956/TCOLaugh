# Base Image
FROM python:3.9-slim

# Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2

# System Dependencies (OpenCV, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1-mesa-glx \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Work Directory
WORKDIR /app

# Python Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Code
COPY . .

# Expose Port
EXPOSE 8000

# Start Command (Default to API, can be overridden for Worker)
CMD ["uvicorn", "panopticon.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
