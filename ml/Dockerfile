FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv==0.12.21

COPY pyproject.toml ./
COPY README.md ./
RUN uv sync --no-dev

COPY api.py ./
COPY occupancy ./occupancy
COPY anomaly ./anomaly
COPY risk ./risk
COPY src ./src

EXPOSE 8100

CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8100"]
