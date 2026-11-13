from .estado import Estado


class Prestamo:
    def __init__(self, id_prestamo, id_usuario, id_ejemplar, fecha_prestamo, fecha_devolucion_estimada,
                 estado=Estado.ACTIVO):
        self.id_prestamo = id_prestamo
        self.id_usuario = id_usuario
        self.id_ejemplar = id_ejemplar
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion_estimada = fecha_devolucion_estimada
        self.estado = estado
