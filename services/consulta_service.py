from datetime import date
from models import Estado
from repositories import usuario_repo, libro_repo, ejemplar_repo, prestamo_repo


class ConsultaService:
    def resumen(self):
        hoy = date.today()
        por_estado = ejemplar_repo.contar_por_estado()
        activos = prestamo_repo.listar_activos()
        return {
            "disponibles": por_estado.get(Estado.DISPONIBLE, 0),
            "prestados": por_estado.get(Estado.PRESTADO, 0),
            "fuera_servicio": por_estado.get(Estado.FUERA_DE_SERVICIO, 0),
            "activos": len(activos),
            "con_retraso": sum(p.fecha_devolucion_estimada < hoy for p in activos),
            "inhabilitados": usuario_repo.contar_inhabilitados(),
        }

    def disponibilidad(self, texto=""):
        """Lista de (libro, [ejemplares]) filtrada por título, autor o ISBN (US-03)."""
        por_titulo = {}
        for e in ejemplar_repo.listar():
            por_titulo.setdefault(e.id_titulo, []).append(e)
        return [(l, por_titulo.get(l.id_titulo, [])) for l in libro_repo.listar(texto)]

    def poseedor(self, codigo):
        """Ejemplar buscado por código y su préstamo activo, si lo tiene (US-10)."""
        e = ejemplar_repo.obtener_por_codigo(codigo)
        if not e:
            return None, None
        return e, prestamo_repo.obtener_activo_de_ejemplar(e.id_ejemplar)

    def historial(self, tipo="usuario", texto=""):
        """Préstamos activos y cerrados filtrados por usuario, título o ejemplar (US-12)."""
        return prestamo_repo.historial(tipo, texto)
