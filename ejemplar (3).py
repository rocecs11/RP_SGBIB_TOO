# SGBIB – Sistema de gestión de préstamos para una biblioteca (Etapa 2)

Python + Flask + HTML/CSS (+ SQLite en la persistencia real).

## Cómo ejecutarlo
```
pip install flask
python app.py          # abrir http://127.0.0.1:5000 (en Windows: py app.py)
```
Usuario de prueba: `admin` / `admin123`

## Estructura (coincide con el diagrama de paquetes)
- `app.py`, `config.py` – arranque y configuración.
- `routes/` – controladores (Blueprints): auth, usuarios, catálogo, préstamos/devoluciones, consultas. `_helpers.py` arma las filas de las tablas.
- `templates/`, `static/css/` – interfaz (Jinja2 + CSS propio).
- `services/` – lógica de negocio. **Ahora son versiones de DEMOSTRACIÓN con datos en memoria (`_demo_datos.py`).**
- `models/` – las 8 clases del diagrama de clases de diseño.

## Integración con la lógica (Alfonso) y la persistencia (Katia)
La interfaz solo usa las instancias de `services/__init__.py` y espera estos métodos.
Para integrar: reemplazar el contenido de `services/` por los servicios reales, o ajustar los nombres en `routes/` y `routes/_helpers.py`.
Los errores de reglas de negocio deben lanzarse como `ReglaNegocioError(mensaje)` (el mensaje se muestra al bibliotecario).

| Servicio | Método esperado | Devuelve |
|---|---|---|
| autenticacion_service | iniciar_sesion(usuario, contrasena) | Bibliotecario o None |
| usuario_service | listar(texto), obtener(id), registrar(nombre, apellido, tipo, identificacion, correo, telefono), cambiar_estado(id, habilitado) | Usuario / lista |
| catalogo_service | listar_libros(texto), obtener_libro(id), registrar_libro(titulo, autor, isbn, editorial, anio, categoria), listar_ejemplares(id_titulo=None), obtener_ejemplar(id), registrar_ejemplar(id_titulo, codigo, ubicacion), cambiar_estado_ejemplar(id, estado, motivo) | Libro / Ejemplar / listas |
| prestamo_service | registrar(id_usuario, id_ejemplar), obtener(id), listar_activos(texto) | Prestamo / lista |
| devolucion_service | registrar(id_prestamo, observaciones, fuera_de_servicio, motivo), de_prestamo(id), retraso_de(id) | (Devolucion, Retraso o None) |
| consulta_service | resumen(), disponibilidad(texto), poseedor(codigo), historial(tipo, texto) | dict / listas |

Pendiente del equipo (US-08): criterio de conteo de los días de retraso (en la demo: días naturales).
