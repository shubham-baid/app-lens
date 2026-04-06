# syntax=docker/dockerfile:1.7

############## Builder: install dependencies ##############
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root

COPY app/ ./app/


############## Runtime: minimal image ##############
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN addgroup --system app \
 && adduser --system --ingroup app --uid 10001 appuser

WORKDIR /app

COPY --from=builder --chown=appuser:app /app/.venv /app/.venv
COPY --from=builder --chown=appuser:app /app/app /app/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c \
      "import urllib.request, sys; \
       r = urllib.request.urlopen('http://localhost:8000/health', timeout=5); \
       sys.exit(0 if r.status == 200 else 1)"

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
