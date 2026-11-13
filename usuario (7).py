"""Clase Estado del diseño: nombres de estado usados por usuarios, ejemplares y préstamos."""


class Estado:
    # Ejemplar (RN-05)
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    FUERA_DE_SERVICIO = "fuera de servicio"
    # Préstamo (RN-15)
    ACTIVO = "activo"
    DEVUELTO = "devuelto"
    # Motivos de fuera de servicio (RN-13)
    MOTIVOS = ("daño", "mantenimiento")

    def __init__(self, id_estado: int, nombre: str, descripcion: str = ""):
        self.id_estado = id_estado
        self.nombre = nombre
        self.descripcion = descripcion
