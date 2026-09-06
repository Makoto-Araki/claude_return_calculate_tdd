FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY apps/ apps/

RUN uv sync --frozen --no-dev --no-editable

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000"]
