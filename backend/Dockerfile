FROM python:3.11-slim

ARG INSTALL_SPEC=.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv

COPY pyproject.toml alembic.ini ./
COPY app/ ./app/
COPY alembic/ ./alembic/
RUN pip install --no-cache-dir "$INSTALL_SPEC"
COPY docker-entrypoint.sh ./

RUN useradd --create-home appuser && mkdir -p /data && chown -R appuser /data /srv
USER appuser
EXPOSE 8000
ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
