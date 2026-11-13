from datetime import date
from models import Devolucion, Retraso, Estado
from repositories import db, ejemplar_repo, prestamo_repo, devolucion_repo
from .errores import ReglaNegocioError


class DevolucionService:
    def registrar(self, id_prestamo, observaciones="", fuera_de_servicio=False, motivo=None):
        with db.transaccion():          # devolución + préstamo cerrado + retraso + estado del ejemplar: todo o nada
            try:
                p = prestamo_repo.obtener(int(id_prestamo))
            except (TypeError, ValueError):
                p = None
            if not p or p.estado != Estado.ACTIVO:
                raise ReglaNegocioError("No existe un préstamo activo para devolver.")
            if fuera_de_servicio and motivo not in Estado.MOTIVOS:
                raise ReglaNegocioError("Indique el motivo: daño o mantenimiento.")
            hoy = date.today()
            d = devolucion_repo.guardar(Devolucion(None, p.id_prestamo, hoy, (observaciones or "").strip()))
            prestamo_repo.marcar_devuelto(p.id_prestamo)                          # RN-11
            retraso = None
            if hoy > p.fecha_devolucion_estimada:                                 # RN-12
                # PENDIENTE DEL EQUIPO (US-08): criterio de conteo de días. Aquí: días naturales de diferencia.
                retraso = devolucion_repo.guardar_retraso(
                    Retraso(None, p.id_prestamo, (hoy - p.fecha_devolucion_estimada).days))
            if fuera_de_servicio:
                ejemplar_repo.actualizar_estado(p.id_ejemplar, Estado.FUERA_DE_SERVICIO, motivo)   # RN-11 / RN-13
            else:
                ejemplar_repo.actualizar_estado(p.id_ejemplar, Estado.DISPONIBLE, None)
            return d, retraso

    def de_prestamo(self, id_prestamo):
        return devolucion_repo.obtener_de_prestamo(id_prestamo)

    def retraso_de(self, id_prestamo):
        return devolucion_repo.retraso_de_prestamo(id_prestamo)
