class Usuario:
    def __init__(self, id_usuario, nombre, apellido, tipo, identificacion, correo="", telefono="", habilitado=True):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.tipo = tipo
        self.identificacion = identificacion
        self.correo = correo
        self.telefono = telefono
        self.habilitado = habilitado

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def comprobar_usuario(self) -> bool:
        return self.habilitado
