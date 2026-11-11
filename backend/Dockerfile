FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# "." for SQLite, ".[postgres]" for the PostgreSQL override.
ARG INSTALL_SPEC=.

COPY pyproject.toml ./
COPY app/ ./app/
RUN pip install --no-cache-dir "$INSTALL_SPEC"

COPY alembic.ini docker-entrypoint.sh ./
COPY alembic/ ./alembic/

RUN useradd --system --create-home appuser \
    && mkdir -p /data \
    && chown -R appuser /app /data
USER appuser

EXPOSE 9000
ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
