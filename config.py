"""Configuración general del prototipo SGBIB."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Clave de sesión de Flask. Para el prototipo basta el valor por defecto;
# si se desea otra, se define la variable de entorno SGBIB_SECRET_KEY (no se escribe aquí).
SECRET_KEY = os.environ.get("SGBIB_SECRET_KEY", "clave-solo-para-prototipo")

NOMBRE_BIBLIOTECA = "Biblioteca Universitaria"
DIAS_PRESTAMO = 7                      # plazo para calcular la fecha establecida de devolución (RN-08)

# Persistencia (SQLite). La ruta puede cambiarse con la variable de entorno SGBIB_DB.
DB_PATH = os.path.join(BASE_DIR, "database", "biblioteca.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
