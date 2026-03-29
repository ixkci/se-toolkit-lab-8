FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} appgroup || true
RUN useradd -u ${APP_UID} -g ${APP_GID} -m -s /bin/bash appuser || true

WORKDIR /app

# Копируем весь репозиторий через additional_contexts
COPY --from=workspace . /app/
RUN chown -R appuser:appgroup /app

USER appuser
WORKDIR /app/nanobot

# Устанавливаем зависимости
RUN rm -rf .venv && uv sync

CMD ["python", "entrypoint.py"]

