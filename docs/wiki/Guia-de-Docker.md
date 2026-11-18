# Guía de Docker

## Dockerfile (multi-stage)

1. **builder**: instala las dependencias de Python en `/install`. Se copia primero `requirements.txt` para reutilizar la capa en caché mientras las dependencias no cambien.
2. **runtime**: parte de una imagen limpia, copia solo `/install` y el código. No lleva caché de pip.

### Decisiones de seguridad y tamaño

| Práctica | Motivo |
|----------|--------|
| `python:3.12-slim` | Imagen base pequeña, menor superficie de ataque |
| Usuario `app` sin privilegios | Un fallo en la app no da acceso root al contenedor |
| `--no-cache-dir` | Evita almacenar caché en la imagen |
| `.dockerignore` | No se envían `.git`, `.env` ni tests al contexto de build |
| `HEALTHCHECK` con librería estándar | Sin instalar `curl` |
| Gunicorn | Servidor apto para producción |
| Versiones fijas | Builds reproducibles |

## docker-compose.yml

- Variables sensibles vía `.env` (no versionado).
- Volumen nombrado para la persistencia.
- Red `backend` aislada.
- `restart: unless-stopped` para recuperación automática.

## Comandos frecuentes

```bash
docker compose up -d --build     # construir y levantar
docker compose ps                # ver estado y salud
docker compose logs -f app       # seguir logs
docker compose exec db psql -U app -d tasks -c "SELECT * FROM tasks;"
docker compose down              # detener conservando datos
docker compose down -v           # detener y borrar datos
docker images                    # ver tamaño de la imagen
```

## Problemas comunes

- **El puerto 8000 está ocupado**: cambia `APP_PORT` en `.env`.
- **Cambié la contraseña y la app no conecta**: el volumen conserva la contraseña anterior; ejecuta `docker compose down -v` y vuelve a levantar.
