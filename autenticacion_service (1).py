from datetime import date, timedelta
import config
from models import Prestamo, Estado
from . import _demo_datos as db
from .errores import ReglaNegocioError


class PrestamoService:
    def registrar(self, id_usuario, id_ejemplar):
        with db.candado:    # un solo préstamo activo por ejemplar aunque lleguen dos solicitudes a la vez (RF-16)
            u = next((x for x in db.usuarios if str(x.id_usuario) == str(id_usuario)), None)
            if not u:
                raise ReglaNegocioError("Seleccione un usuario registrado.")
            if not u.habilitado:                                                  # RN-06
                raise ReglaNegocioError(f"{u.nombre_completo} está inhabilitado y no puede iniciar un préstamo.")
            e = next((x for x in db.ejemplares if str(x.id_ejemplar) == str(id_ejemplar)), None)
            if not e:
                raise ReglaNegocioError("Seleccione un ejemplar registrado.")
            if e.estado == Estado.PRESTADO or any(p.id_ejemplar == e.id_ejemplar and p.estado == Estado.ACTIVO for p in db.prestamos):
                raise ReglaNegocioError(f"El ejemplar {e.codigo} no está disponible: ya tiene un préstamo activo.")   # RN-10
            if e.estado != Estado.DISPONIBLE:                                     # RN-07
                raise ReglaNegocioError(f"El ejemplar {e.codigo} no está disponible (está {e.estado}).")
            hoy = date.today()
            p = Prestamo(db.siguiente_id(db.prestamos, "id_prestamo"), u.id_usuario, e.id_ejemplar, hoy,
                         hoy + timedelta(days=config.DIAS_PRESTAMO))              # RN-08
            db.prestamos.append(p)
            e.estado = Estado.PRESTADO                                            # RN-09
            return p

    def obtener(self, id_prestamo):
        return next((p for p in db.prestamos if p.id_prestamo == int(id_prestamo)), None)

    def listar_activos(self, texto=""):
        """Préstamos activos (RN-15). `texto` filtra por usuario o ejemplar."""
        activos = [p for p in db.prestamos if p.estado == Estado.ACTIVO]
        t = (texto or "").strip().lower()
        if not t:
            return activos
        res = []
        for p in activos:
            u = next(x for x in db.usuarios if x.id_usuario == p.id_usuario)
            e = next(x for x in db.ejemplares if x.id_ejemplar == p.id_ejemplar)
            l = next(x for x in db.libros if x.id_titulo == e.id_titulo)
            if t in f"{u.nombre} {u.apellido} {u.identificacion} {e.codigo} {l.titulo}".lower():
                res.append(p)
        return res
