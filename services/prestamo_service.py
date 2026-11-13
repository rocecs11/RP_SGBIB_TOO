import sqlite3
from datetime import date, timedelta
import config
from models import Prestamo, Estado
from repositories import db, usuario_repo, ejemplar_repo, prestamo_repo
from .errores import ReglaNegocioError


def _a_int(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


class PrestamoService:
    def registrar(self, id_usuario, id_ejemplar):
        # Transacción con bloqueo de escritura: validar + guardar préstamo + marcar ejemplar es todo o nada, y dos
        # solicitudes simultáneas se atienden una tras otra (RF-16). El índice único de la BD es la garantía final.
        try:
            with db.transaccion():
                u = usuario_repo.obtener(_a_int(id_usuario) or 0)
                if not u:
                    raise ReglaNegocioError("Seleccione un usuario registrado.")
                if not u.habilitado:                                              # RN-06
                    raise ReglaNegocioError(f"{u.nombre_completo} está inhabilitado y no puede iniciar un préstamo.")
                e = ejemplar_repo.obtener(_a_int(id_ejemplar) or 0)
                if not e:
                    raise ReglaNegocioError("Seleccione un ejemplar registrado.")
                if e.estado == Estado.PRESTADO or prestamo_repo.obtener_activo_de_ejemplar(e.id_ejemplar):
                    raise ReglaNegocioError(f"El ejemplar {e.codigo} no está disponible: ya tiene un préstamo activo.")   # RN-10
                if e.estado != Estado.DISPONIBLE:                                 # RN-07
                    raise ReglaNegocioError(f"El ejemplar {e.codigo} no está disponible (está {e.estado}).")
                hoy = date.today()
                p = Prestamo(None, u.id_usuario, e.id_ejemplar, hoy, hoy + timedelta(days=config.DIAS_PRESTAMO))   # RN-08
                prestamo_repo.guardar(p)
                ejemplar_repo.actualizar_estado(e.id_ejemplar, Estado.PRESTADO)   # RN-09
                return p
        except sqlite3.IntegrityError:
            raise ReglaNegocioError("El ejemplar ya tiene un préstamo activo.")

    def obtener(self, id_prestamo):
        try:
            return prestamo_repo.obtener(id_prestamo)
        except (TypeError, ValueError):
            return None

    def listar_activos(self, texto=""):
        """Préstamos activos (RN-15). `texto` filtra por usuario, ejemplar o título."""
        return prestamo_repo.listar_activos(texto)
