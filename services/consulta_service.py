from datetime import date
from models import Estado
from . import _demo_datos as db


class ConsultaService:
    def resumen(self):
        hoy = date.today()
        activos = [p for p in db.prestamos if p.estado == Estado.ACTIVO]
        return {
            "disponibles": sum(e.estado == Estado.DISPONIBLE for e in db.ejemplares),
            "prestados": sum(e.estado == Estado.PRESTADO for e in db.ejemplares),
            "fuera_servicio": sum(e.estado == Estado.FUERA_DE_SERVICIO for e in db.ejemplares),
            "activos": len(activos),
            "con_retraso": sum(p.fecha_devolucion_estimada < hoy for p in activos),
            "inhabilitados": sum(not u.habilitado for u in db.usuarios),
        }

    def disponibilidad(self, texto=""):
        """Lista de (libro, [ejemplares]) filtrada por título, autor o ISBN (US-03)."""
        t = (texto or "").strip().lower()
        res = []
        for l in db.libros:
            if t and t not in f"{l.titulo} {l.autor} {l.isbn}".lower():
                continue
            res.append((l, [e for e in db.ejemplares if e.id_titulo == l.id_titulo]))
        return res

    def poseedor(self, codigo):
        """Ejemplar buscado por código y su préstamo activo, si lo tiene (US-10)."""
        codigo = (codigo or "").strip().lower()
        e = next((x for x in db.ejemplares if x.codigo.lower() == codigo), None)
        if not e:
            return None, None
        p = next((x for x in db.prestamos if x.id_ejemplar == e.id_ejemplar and x.estado == Estado.ACTIVO), None)
        return e, p

    def historial(self, tipo="usuario", texto=""):
        """Préstamos activos y cerrados filtrados por usuario, título o ejemplar (US-12)."""
        t = (texto or "").strip().lower()
        res = []
        for p in db.prestamos:
            u = next(x for x in db.usuarios if x.id_usuario == p.id_usuario)
            e = next(x for x in db.ejemplares if x.id_ejemplar == p.id_ejemplar)
            l = next(x for x in db.libros if x.id_titulo == e.id_titulo)
            campo = {"usuario": f"{u.nombre} {u.apellido} {u.identificacion}",
                     "titulo": f"{l.titulo} {l.autor}", "ejemplar": e.codigo}.get(tipo, "")
            if not t or t in campo.lower():
                res.append(p)
        return sorted(res, key=lambda x: x.fecha_prestamo, reverse=True)
