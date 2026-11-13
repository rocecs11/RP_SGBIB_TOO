class Retraso:
    def __init__(self, id_retraso, id_prestamo, dias_retraso, estado="registrado"):
        self.id_retraso = id_retraso
        self.id_prestamo = id_prestamo
        self.dias_retraso = dias_retraso
        self.estado = estado
