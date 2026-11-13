from .estado import Estado


class Ejemplar:
    def __init__(self, id_ejemplar, id_titulo, codigo, fecha_adquisicion=None, ubicacion="",
                 estado=Estado.DISPONIBLE, motivo=None):
        self.id_ejemplar = id_ejemplar
        self.id_titulo = id_titulo
        self.codigo = codigo
        self.fecha_adquisicion = fecha_adquisicion
        self.ubicacion = ubicacion
        self.estado = estado
        self.motivo = motivo          # daño / mantenimiento cuando está fuera de servicio (RN-13)

    def comprobar_disponibilidad(self) -> bool:
        return self.estado == Estado.DISPONIBLE
