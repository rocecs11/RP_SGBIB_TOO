-- ============================================================
-- SGBIB - Esquema de la base de datos SQLite (biblioteca.db)
-- Se ejecuta con database/init_db.py (o automáticamente al
-- primer arranque si el archivo .db no existe).
-- Es seguro ejecutarlo varias veces (IF NOT EXISTS).
-- Los estados se guardan como texto con CHECK; los valores
-- coinciden con las constantes de models/estado.py.
-- ============================================================

PRAGMA foreign_keys = ON;

-- Personal bibliotecario que accede al sistema (la contraseña se guarda CIFRADA, nunca en claro)
CREATE TABLE IF NOT EXISTS bibliotecario (
    id_bibliotecario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT NOT NULL,
    usuario          TEXT NOT NULL UNIQUE COLLATE NOCASE,
    contrasena       TEXT NOT NULL                       -- hash (werkzeug), no texto plano
);

-- Usuarios (lectores) de la biblioteca                         RF-01 a RF-05
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT NOT NULL,
    apellido       TEXT NOT NULL,
    tipo           TEXT NOT NULL DEFAULT 'Estudiante',
    identificacion TEXT NOT NULL UNIQUE COLLATE NOCASE,     -- RN-01: sin duplicados
    correo         TEXT NOT NULL DEFAULT '',
    telefono       TEXT NOT NULL DEFAULT '',
    habilitado     INTEGER NOT NULL DEFAULT 1               -- RN-02: nace habilitado
                   CHECK (habilitado IN (0, 1))
);

-- Títulos (datos bibliográficos)                               RF-06
CREATE TABLE IF NOT EXISTS libro (
    id_titulo        INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn             TEXT NOT NULL UNIQUE,
    titulo           TEXT NOT NULL,
    autor            TEXT NOT NULL,
    editorial        TEXT NOT NULL DEFAULT '',
    anio_publicacion INTEGER,
    categoria        TEXT NOT NULL DEFAULT ''
);

-- Ejemplares físicos de un título                              RF-07 a RF-11
CREATE TABLE IF NOT EXISTS ejemplar (
    id_ejemplar       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_titulo         INTEGER NOT NULL REFERENCES libro(id_titulo),
    codigo            TEXT NOT NULL UNIQUE COLLATE NOCASE,
    fecha_adquisicion TEXT,                                 -- ISO 'AAAA-MM-DD'
    ubicacion         TEXT NOT NULL DEFAULT '',
    estado            TEXT NOT NULL DEFAULT 'disponible'    -- RN-04 / RN-05
                      CHECK (estado IN ('disponible', 'prestado', 'fuera de servicio')),
    motivo            TEXT                                  -- RN-13: solo si está fuera de servicio
                      CHECK (motivo IS NULL OR motivo IN ('daño', 'mantenimiento')),
    CHECK (estado = 'fuera de servicio' OR motivo IS NULL)
);

-- Préstamos                                                    RF-12 a RF-16
CREATE TABLE IF NOT EXISTS prestamo (
    id_prestamo               INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario                INTEGER NOT NULL REFERENCES usuario(id_usuario),
    id_ejemplar               INTEGER NOT NULL REFERENCES ejemplar(id_ejemplar),
    fecha_prestamo            TEXT NOT NULL,
    fecha_devolucion_estimada TEXT NOT NULL,
    estado                    TEXT NOT NULL DEFAULT 'activo'  -- RN-15
                              CHECK (estado IN ('activo', 'devuelto'))
);

-- RN-10 / RF-15 / RF-16: como máximo UN préstamo activo por ejemplar.
-- Es la garantía final ante solicitudes simultáneas.
CREATE UNIQUE INDEX IF NOT EXISTS ux_prestamo_activo_por_ejemplar
    ON prestamo(id_ejemplar) WHERE estado = 'activo';

CREATE INDEX IF NOT EXISTS ix_prestamo_usuario  ON prestamo(id_usuario);
CREATE INDEX IF NOT EXISTS ix_prestamo_ejemplar ON prestamo(id_ejemplar);
CREATE INDEX IF NOT EXISTS ix_ejemplar_titulo   ON ejemplar(id_titulo);

-- Devoluciones (una por préstamo)                              RF-17 a RF-19
CREATE TABLE IF NOT EXISTS devolucion (
    id_devolucion    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prestamo      INTEGER NOT NULL UNIQUE REFERENCES prestamo(id_prestamo),
    fecha_devolucion TEXT NOT NULL,
    observaciones    TEXT NOT NULL DEFAULT ''
);

-- Retrasos (uno por préstamo devuelto tarde; NO guarda dinero) RF-20 a RF-22
CREATE TABLE IF NOT EXISTS retraso (
    id_retraso   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prestamo  INTEGER NOT NULL UNIQUE REFERENCES prestamo(id_prestamo),
    dias_retraso INTEGER NOT NULL CHECK (dias_retraso > 0),
    estado       TEXT NOT NULL DEFAULT 'registrado'
);
