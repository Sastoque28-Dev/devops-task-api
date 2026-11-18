# CI/CD con GitHub Actions

Archivo: `.github/workflows/ci.yml`

## Disparadores

- `pull_request` hacia `main`: valida cada PR.
- `push` a `main`: valida y publica la imagen.
- `push` de tags `v*`: publica la imagen con la versión.

## Jobs

| Job | Qué hace | Cuándo |
|-----|----------|--------|
| `test` | Instala dependencias y ejecuta `pytest` | Siempre |
| `docker` | Copia `.env.example`, ejecuta `docker compose up --build --wait`, prueba `/health`, `/health/db` y `/tasks`, y apaga todo | Tras `test` |
| `publish` | Construye y sube la imagen a `ghcr.io/<usuario>/<repo>` con tags `latest`, versión semántica y SHA | Solo en `main` o tags |

## Seguridad

- Se usa `GITHUB_TOKEN` (sin secretos manuales) con permisos mínimos: `contents: read` y `packages: write`.
- Las acciones están fijadas a versiones mayores estables.

## Cómo ver los resultados

Pestaña **Actions** del repositorio, o el badge del README. Si un job falla, el paso "Logs si falla" imprime `docker compose logs`.

## Versionado

```bash
git tag -a v1.0.0 -m "Primera versión estable"
git push origin v1.0.0
```
