FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/.venv

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv && \
    uv venv && \
    uv sync

COPY . .

EXPOSE 8000
