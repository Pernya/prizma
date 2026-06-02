FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY triton-model-repository ./triton-model-repository

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/data/artifacts /app/state/jobs \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "prizma_backend.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
