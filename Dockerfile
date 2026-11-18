# syntax=docker/dockerfile:1

# ---------- Etapa 1: builder ----------
# Instala dependencias aparte para que la imagen final no lleve caché de pip
# ni herramientas de compilación.
FROM python:3.12-slim AS builder

WORKDIR /build

# Se copia primero solo requirements.txt: mientras no cambien las
# dependencias, Docker reutiliza esta capa (builds mucho más rápidos).
COPY src/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Etapa 2: runtime ----------
FROM python:3.12-slim AS runtime

# PYTHONUNBUFFERED: los logs salen en tiempo real a `docker logs`.
# PYTHONDONTWRITEBYTECODE: evita archivos .pyc innecesarios en la imagen.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Seguridad: usuario sin privilegios (nunca ejecutar como root).
RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=app:app src/ .

USER app

EXPOSE 8000

# Healthcheck con la librería estándar (no hace falta instalar curl).
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"

# Gunicorn en lugar del servidor de desarrollo de Flask.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
