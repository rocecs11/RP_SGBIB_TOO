import sqlite3
from datetime import date
from models import Libro, Ejemplar, Estado
from repositories import libro_repo, ejemplar_repo
from .errores import ReglaNegocioError


class CatalogoService:
    def listar_libros(self, texto=""):
        return libro_repo.listar(texto)

    def obtener_libro(self, id_titulo):
        try:
            return libro_repo.obtener(id_titulo)
        except (TypeError, ValueError):
            return None

    def registrar_libro(self, titulo, autor, isbn, editorial="", anio_publicacion=None, categoria=""):
        titulo, autor, isbn = (titulo or "").strip(), (autor or "").strip(), (isbn or "").strip()
        if not titulo or not autor or not isbn:
            raise ReglaNegocioError("Título, autor e ISBN son obligatorios.")
        if libro_repo.obtener_por_isbn(isbn):
            raise ReglaNegocioError(f"Ya existe un título con el ISBN {isbn}.")
        try:
            anio = int(anio_publicacion) if anio_publicacion else None
        except ValueError:
            raise ReglaNegocioError("El año de publicación debe ser un número.")
        l = Libro(None, isbn, titulo, autor, (editorial or "").strip(), anio, (categoria or "").strip())
        try:
            return libro_repo.guardar(l)
        except sqlite3.IntegrityError:
            raise ReglaNegocioError(f"Ya existe un título con el ISBN {isbn}.")

    def listar_ejemplares(self, id_titulo=None):
        return ejemplar_repo.listar(id_titulo)

    def obtener_ejemplar(self, id_ejemplar):
        try:
            return ejemplar_repo.obtener(id_ejemplar)
        except (TypeError, ValueError):
            return None

    def registrar_ejemplar(self, id_titulo, codigo, ubicacion=""):
        codigo = (codigo or "").strip()
        if not self.obtener_libro(id_titulo):
            raise ReglaNegocioError("El título no existe.")
        if not codigo:
            raise ReglaNegocioError("El código del ejemplar es obligatorio.")
        if ejemplar_repo.obtener_por_codigo(codigo):
            raise ReglaNegocioError(f"Ya existe un ejemplar con el código {codigo}.")
        e = Ejemplar(None, int(id_titulo), codigo, date.today(), (ubicacion or "").strip(), Estado.DISPONIBLE)   # RN-04
        try:
            return ejemplar_repo.guardar(e)
        except sqlite3.IntegrityError:
            raise ReglaNegocioError(f"Ya existe un ejemplar con el código {codigo}.")

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
        ejemplar_repo.actualizar_estado(e.id_ejemplar, e.estado, e.motivo)
        return e
