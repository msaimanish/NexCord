FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv==0.12.21

COPY pyproject.toml ./
COPY README.md ./
COPY src ./src

RUN uv sync --no-dev

COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000 8001

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]