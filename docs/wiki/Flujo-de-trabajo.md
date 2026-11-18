# Flujo de trabajo en Git (GitHub Flow)

## Ramas

- `main`: siempre estable y desplegable.
- `feature/<nombre>`: nuevas funcionalidades o infraestructura.
- `docs/<nombre>`: documentación.

## Ciclo

1. Crear un Issue con criterios de aceptación.
2. `git checkout -b feature/<nombre>` desde `main` actualizado.
3. Commits pequeños con mensajes tipo Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`, `test:`, `chore:`).
4. Abrir un Pull Request con la plantilla y `Closes #N`.
5. Esperar el CI en verde y fusionar (merge).
6. Eliminar la rama.

## Ejemplo de mensajes

```
feat(api): agrega endpoints CRUD de tareas
test: cubre validaciones y errores de base de datos
build(docker): Dockerfile multi-stage con usuario no root
ci: agrega workflow de pruebas e integración con Compose
```
