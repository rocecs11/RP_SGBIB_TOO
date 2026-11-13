from datetime import date
from models import Libro, Ejemplar, Estado
from . import _demo_datos as db
from .errores import ReglaNegocioError


class CatalogoService:
    def listar_libros(self, texto=""):
        t = (texto or "").strip().lower()
        return [l for l in db.libros if not t or t in f"{l.titulo} {l.autor} {l.isbn}".lower()]

    def obtener_libro(self, id_titulo):
        return next((l for l in db.libros if l.id_titulo == int(id_titulo)), None)

    def registrar_libro(self, titulo, autor, isbn, editorial="", anio_publicacion=None, categoria=""):
        titulo, autor, isbn = (titulo or "").strip(), (autor or "").strip(), (isbn or "").strip()
        if not titulo or not autor or not isbn:
            raise ReglaNegocioError("Título, autor e ISBN son obligatorios.")
        if any(l.isbn == isbn for l in db.libros):
            raise ReglaNegocioError(f"Ya existe un título con el ISBN {isbn}.")
        try:
            anio = int(anio_publicacion) if anio_publicacion else None
        except ValueError:
            raise ReglaNegocioError("El año de publicación debe ser un número.")
        l = Libro(db.siguiente_id(db.libros, "id_titulo"), isbn, titulo, autor, (editorial or "").strip(), anio, (categoria or "").strip())
        db.libros.append(l)
        return l

    def listar_ejemplares(self, id_titulo=None):
        return [e for e in db.ejemplares if id_titulo is None or e.id_titulo == int(id_titulo)]

    def obtener_ejemplar(self, id_ejemplar):
        return next((e for e in db.ejemplares if e.id_ejemplar == int(id_ejemplar)), None)

    def registrar_ejemplar(self, id_titulo, codigo, ubicacion=""):
        codigo = (codigo or "").strip()
        if not self.obtener_libro(id_titulo):
            raise ReglaNegocioError("El título no existe.")
        if not codigo:
            raise ReglaNegocioError("El código del ejemplar es obligatorio.")
        if any(e.codigo.lower() == codigo.lower() for e in db.ejemplares):
            raise ReglaNegocioError(f"Ya existe un ejemplar con el código {codigo}.")
        e = Ejemplar(db.siguiente_id(db.ejemplares, "id_ejemplar"), int(id_titulo), codigo, date.today(),
                     (ubicacion or "").strip(), Estado.DISPONIBLE)                 # RN-04
        db.ejemplares.append(e)
        return e

    def cambiar_estado_ejemplar(self, id_ejemplar, nuevo_estado, motivo=None):
        e = self.obtener_ejemplar(id_ejemplar)
        if not e:
            raise ReglaNegocioError("El ejemplar no existe.")
        if e.estado == Estado.PRESTADO:
            raise ReglaNegocioError("El ejemplar está prestado: primero registre su devolución.")
        if nuevo_estado == Estado.FUERA_DE_SERVICIO:
            if motivo not in Estado.MOTIVOS:                                     # RN-13
                raise ReglaNegocioError("Indique el motivo: daño o mantenimiento.")
            e.estado, e.motivo = Estado.FUERA_DE_SERVICIO, motivo
        elif nuevo_estado == Estado.DISPONIBLE:                                  # RN-14
            e.estado, e.motivo = Estado.DISPONIBLE, None
        else:
            raise ReglaNegocioError("Estado no permitido.")
        return e
