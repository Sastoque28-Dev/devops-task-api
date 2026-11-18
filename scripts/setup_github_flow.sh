#!/usr/bin/env bash
# Crea el repositorio en GitHub y reproduce un flujo profesional:
# 6 Issues -> 6 ramas -> 6 Pull Requests fusionados -> tag v1.0.0.
#
# Requisitos: git, GitHub CLI (gh) autenticado (`gh auth login`).
# Uso (desde la raíz del proyecto):  ./scripts/setup_github_flow.sh nombre-del-repo
set -euo pipefail

REPO_NAME="${1:?Uso: ./scripts/setup_github_flow.sh nombre-del-repo}"
command -v gh >/dev/null || { echo "Instala GitHub CLI: https://cli.github.com"; exit 1; }
gh auth status >/dev/null

# Guardamos el README final y dejamos uno mínimo para el commit inicial.
cp README.md /tmp/README.final.md
printf '# %s\n' "$REPO_NAME" > README.md

git init -b main
git add .gitignore README.md
git commit -m "chore: commit inicial con .gitignore y README"
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
FULL_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

new_issue() { gh issue create --title "$1" --body "$2" | awk -F/ '{print $NF}'; }

I1=$(new_issue "API REST de tareas con Flask" "Implementar endpoints /health, /tasks y pruebas unitarias.")
I2=$(new_issue "Dockerfile optimizado" "Build multi-stage, usuario no root, healthcheck y .dockerignore.")
I3=$(new_issue "Orquestar app y base de datos con Compose" "Servicios app y db, red, volumen, variables de entorno y depends_on con healthcheck.")
I4=$(new_issue "Pipeline CI/CD con GitHub Actions" "Pruebas, integración con Compose y publicación de imagen en GHCR.")
I5=$(new_issue "Plantillas de Issues y Pull Requests" "Estandarizar la colaboración con plantillas en .github/.")
I6=$(new_issue "Documentación: README, Wiki y scripts" "README con badges, páginas de la Wiki y script de automatización.")

finish_pr() { # rama, título, issue, resumen
  git push -u origin "$1"
  gh pr create --base main --head "$1" --title "$2" \
    --body "## Descripción
$4

Closes #$3"
  gh pr merge "$1" --merge --delete-branch
  git checkout main && git pull origin main
}

# PR 1 · API
git checkout -b feature/api-tareas
git add src/app.py src/requirements.txt
git commit -m "feat(api): agrega endpoints de salud y CRUD de tareas"
git add requirements-dev.txt pytest.ini tests
git commit -m "test: pruebas unitarias con base de datos simulada"
finish_pr feature/api-tareas "feat: API REST de tareas" "$I1" "API Flask con endpoints de salud y tareas, más pruebas unitarias."

# PR 2 · Dockerfile
git checkout -b feature/dockerfile
git add Dockerfile .dockerignore
git commit -m "build(docker): Dockerfile multi-stage con usuario no root y healthcheck"
finish_pr feature/dockerfile "build: Dockerfile optimizado" "$I2" "Imagen multi-stage basada en python:3.12-slim."

# PR 3 · Compose
git checkout -b feature/docker-compose
git add docker-compose.yml .env.example
git commit -m "build(compose): servicios app y db con red, volumen y healthchecks"
git add db
git commit -m "feat(db): script de inicialización de la tabla tasks"
finish_pr feature/docker-compose "build: orquestación con Docker Compose" "$I3" "Compose con app + PostgreSQL, red backend y volumen pgdata."

# PR 4 · CI
git checkout -b feature/github-actions
git add .github/workflows
git commit -m "ci: workflow de pruebas, integración con Compose y publicación en GHCR"
finish_pr feature/github-actions "ci: pipeline con GitHub Actions" "$I4" "Jobs test, docker y publish."

# PR 5 · Plantillas
git checkout -b feature/plantillas
git add .github/ISSUE_TEMPLATE .github/PULL_REQUEST_TEMPLATE.md
git commit -m "chore(github): plantillas de Issues y Pull Requests"
finish_pr feature/plantillas "chore: plantillas de Issues y PR" "$I5" "Plantillas de bug, feature y Pull Request."

# PR 6 · Documentación
git checkout -b docs/readme-wiki
cp /tmp/README.final.md README.md
sed -i "s#USUARIO/REPO#${FULL_REPO}#g; s#REPO.git#${REPO_NAME}.git#g" README.md
git add README.md
git commit -m "docs: README completo con badges, uso y estructura"
git add docs scripts LICENSE
git commit -m "docs: páginas de la Wiki, informe técnico y script de flujo"
finish_pr docs/readme-wiki "docs: README, Wiki y scripts" "$I6" "Documentación completa del proyecto."

git tag -a v1.0.0 -m "Primera versión estable"
git push origin v1.0.0

echo
echo "Listo. Repositorio: https://github.com/${FULL_REPO}"
echo "Siguiente paso manual: crear la Wiki y copiar docs/wiki/*.md (ver docs/GUIA_ENTREGA.md)."
