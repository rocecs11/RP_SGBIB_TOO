from datetime import date
from models import Devolucion, Retraso, Estado
from . import _demo_datos as db
from .errores import ReglaNegocioError


class DevolucionService:
    def registrar(self, id_prestamo, observaciones="", fuera_de_servicio=False, motivo=None):
        p = next((x for x in db.prestamos if str(x.id_prestamo) == str(id_prestamo)), None)
        if not p or p.estado != Estado.ACTIVO:
            raise ReglaNegocioError("No existe un préstamo activo para devolver.")
        if fuera_de_servicio and motivo not in Estado.MOTIVOS:
            raise ReglaNegocioError("Indique el motivo: daño o mantenimiento.")
        hoy = date.today()
        d = Devolucion(db.siguiente_id(db.devoluciones, "id_devolucion"), p.id_prestamo, hoy, (observaciones or "").strip())
        db.devoluciones.append(d)
        p.estado = Estado.DEVUELTO                                                # RN-11
        retraso = None
        if hoy > p.fecha_devolucion_estimada:                                     # RN-12
            # PENDIENTE DEL EQUIPO (US-08): criterio de conteo de días. Aquí: días naturales de diferencia.
            retraso = Retraso(db.siguiente_id(db.retrasos, "id_retraso"), p.id_prestamo, (hoy - p.fecha_devolucion_estimada).days)
            db.retrasos.append(retraso)
        e = next(x for x in db.ejemplares if x.id_ejemplar == p.id_ejemplar)
        if fuera_de_servicio:
            e.estado, e.motivo = Estado.FUERA_DE_SERVICIO, motivo                 # RN-11 / RN-13
        else:
            e.estado, e.motivo = Estado.DISPONIBLE, None
        return d, retraso

    def de_prestamo(self, id_prestamo):
        return next((d for d in db.devoluciones if d.id_prestamo == id_prestamo), None)

    def retraso_de(self, id_prestamo):
        return next((r for r in db.retrasos if r.id_prestamo == id_prestamo), None)
