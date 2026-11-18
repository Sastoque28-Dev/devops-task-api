-- Se ejecuta automáticamente la primera vez que se crea el volumen de datos.
CREATE TABLE IF NOT EXISTS tasks (
    id    SERIAL PRIMARY KEY,
    title TEXT    NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title) VALUES
    ('Contenerizar la aplicación'),
    ('Configurar GitHub Actions');
