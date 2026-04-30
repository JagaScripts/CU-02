# Build etapa
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar la librería compartida en la ruta raíz para que coincida con ../lib-shared-kernel
COPY services/lib-shared-kernel /lib-shared-kernel
COPY services/CU-02/pyproject.toml services/CU-02/uv.lock* /app/

# Sincronizar dependencias
RUN uv sync --frozen --no-install-project

# Etapa final
FROM python:3.12-slim

WORKDIR /app

# Copiar el entorno virtual y el código
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /lib-shared-kernel /lib-shared-kernel
COPY services/CU-02/app /app/app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:/lib-shared-kernel"

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
