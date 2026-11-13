# SGBIB – Sistema de gestión de préstamos para una biblioteca (Etapa 2)

Python + Flask + HTML/CSS + SQLite. Los datos se guardan en `database/biblioteca.db` y sobreviven al cierre del programa.

## Requisitos
- Python 3.10 o superior (probado con 3.13) y `pip`.
- Un navegador web (Chrome, Edge o Firefox).

## Instalar y ejecutar
```
pip install -r requirements.txt        # instala Flask
python app.py                          # en Windows: py app.py
```
Abrir http://127.0.0.1:5000 · usuario de prueba: `admin` / `admin123` (solo pruebas).

Al primer arranque `biblioteca.db` se crea sola (tablas de `database/schema.sql` + usuario `admin`), pero **vacía**.
Para cargar datos de ejemplo (usuarios, títulos, ejemplares, préstamos, un retraso):
```
python database/init_db.py --demo
```
Otras opciones: `--reset` borra la base y la crea de nuevo (`--reset --demo` = base nueva con ejemplos).
Detener el servidor con Ctrl+C. Al volver a ejecutar, la información sigue ahí.

## Configuración (opcional, variables de entorno)
| Variable | Efecto |
|---|---|
| `SGBIB_DB` | Ruta alternativa del archivo `.db` |
| `SGBIB_ADMIN_PASSWORD` | Contraseña inicial de `admin` (antes de crear la base) |
| `SGBIB_SECRET_KEY` | Clave de sesión de Flask |

No hay contraseñas reales ni claves privadas en el código; la contraseña del bibliotecario se guarda cifrada.

## Pruebas
```
python -m unittest discover -s tests -v
```
Usan una base temporal; no tocan `biblioteca.db`.

## Estructura (coincide con los diagramas de paquetes y componentes)
- `app.py`, `config.py` – arranque y configuración.
- `routes/` – controladores (Blueprints). `templates/`, `static/css/` – interfaz.
- `services/` – lógica de negocio (reglas RN-01 a RN-15); no escriben SQL.
- `models/` – las 8 clases del diseño.
- `repositories/` – persistencia: `db.py` (conexión y transacciones) y un repositorio por entidad (retrasos van en `DevolucionRepository`).
- `database/` – `schema.sql` (tablas), `init_db.py` (crear/reiniciar/cargar ejemplos), `biblioteca.db` (se genera).
- `tests/` – pruebas de persistencia, reglas y flujo web.

Pendiente del equipo (US-08): criterio de conteo de los días de retraso (ahora: días naturales).
