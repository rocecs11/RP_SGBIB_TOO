import sqlite3
from models import Usuario
from repositories import usuario_repo
from .errores import ReglaNegocioError


class UsuarioService:
    def listar(self, texto=""):
        return usuario_repo.listar(texto)

    def obtener(self, id_usuario):
        try:
            return usuario_repo.obtener(id_usuario)
        except (TypeError, ValueError):
            return None

    def registrar(self, nombre, apellido, tipo, identificacion, correo="", telefono=""):
        nombre, apellido, identificacion = (nombre or "").strip(), (apellido or "").strip(), (identificacion or "").strip()
        if not nombre or not apellido or not identificacion:
            raise ReglaNegocioError("Nombre, apellido e identificación son obligatorios.")
        if usuario_repo.obtener_por_identificacion(identificacion):                       # RN-01
            raise ReglaNegocioError(f"Ya existe un usuario con la identificación {identificacion}.")
        u = Usuario(None, nombre, apellido, tipo or "Estudiante", identificacion,
                    (correo or "").strip(), (telefono or "").strip(), True)               # RN-02
        try:
            return usuario_repo.guardar(u)
        except sqlite3.IntegrityError:        # otra solicitud la registró justo antes (la BD lo impide)
            raise ReglaNegocioError(f"Ya existe un usuario con la identificación {identificacion}.")

    def cambiar_estado(self, id_usuario, habilitado):
        u = self.obtener(id_usuario)
        if not u:
            raise ReglaNegocioError("El usuario no existe.")
        usuario_repo.actualizar_estado(u.id_usuario, habilitado)
        u.habilitado = bool(habilitado)
        return u
