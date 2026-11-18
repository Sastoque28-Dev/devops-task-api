# Guía de entrega paso a paso

## 1. Probar localmente
```bash
cp .env.example .env
docker compose up -d --build
curl localhost:8000/health/db
```
Toma capturas de: `docker compose ps` (servicios *healthy*), `curl` a `/tasks`, `docker images` y, si quieres, `docker compose down` + `up` para demostrar que los datos persisten.
Guárdalas en `docs/informe/capturas/` con los nombres `01_compose.png`, `02_api.png`, `03_actions.png`.

## 2. Crear el repositorio y el flujo
```bash
gh auth login
./scripts/setup_github_flow.sh nombre-del-repo
```
Esto deja 6 Issues cerrados, 6 PRs fusionados, commits descriptivos y el tag `v1.0.0`.

## 3. Wiki (3 páginas mínimo; aquí hay 5)
GitHub crea el repo de la Wiki solo al guardar la primera página desde la web:
1. En tu repo: pestaña **Wiki** > **Create the first page** > guarda cualquier texto.
2. Luego:
```bash
git clone https://github.com/USUARIO/REPO.wiki.git
cp docs/wiki/*.md REPO.wiki/
cd REPO.wiki && git add . && git commit -m "docs: páginas iniciales" && git push
```

## 4. Informe técnico
Con las capturas en su carpeta:
```bash
pip install reportlab
python docs/informe/generar_informe.py
```
Edita tu nombre y datos al inicio del script. Verifica que quede en 2-3 páginas.

## 5. Demostración
Graba un video corto (2-4 min): `docker compose up`, pruebas con curl, pestaña Actions en verde, lista de PRs/Issues cerrados.

## 6. Qué entregar
- Enlace al repositorio (público) y a la Wiki.
- PDF del informe.
- Enlace o archivo del video de demostración.
