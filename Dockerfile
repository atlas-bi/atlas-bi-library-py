# Root Dockerfile for CI/Coolify multi-target builds.
# Targets:
# - api: builds the Django API image from ./backend
# - web: builds the Next.js app image from ./frontend

FROM python:3.13-slim-bookworm AS api

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/.venv

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./

RUN pip install uv && \
    uv venv && \
    uv sync

COPY backend/ ./

EXPOSE 8000


FROM node:21 AS web

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm install -g pnpm

WORKDIR /app

COPY frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml frontend/package.json ./
COPY frontend/apps/web/package.json ./apps/web/package.json
COPY frontend/packages/types/package.json ./packages/types/package.json
COPY frontend/packages/ui/package.json ./packages/ui/package.json

RUN pnpm install -r --frozen-lockfile

COPY frontend/ ./

EXPOSE 3000
