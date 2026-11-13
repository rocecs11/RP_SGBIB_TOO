from models import Usuario
from . import _demo_datos as db
from .errores import ReglaNegocioError


class UsuarioService:
    def listar(self, texto=""):
        t = (texto or "").strip().lower()
        return [u for u in db.usuarios
                if not t or t in f"{u.nombre} {u.apellido} {u.identificacion} {u.correo}".lower()]

    def obtener(self, id_usuario):
        return next((u for u in db.usuarios if u.id_usuario == int(id_usuario)), None)

    def registrar(self, nombre, apellido, tipo, identificacion, correo="", telefono=""):
        nombre, apellido, identificacion = (nombre or "").strip(), (apellido or "").strip(), (identificacion or "").strip()
        if not nombre or not apellido or not identificacion:
            raise ReglaNegocioError("Nombre, apellido e identificación son obligatorios.")
        if any(u.identificacion.lower() == identificacion.lower() for u in db.usuarios):   # RN-01
            raise ReglaNegocioError(f"Ya existe un usuario con la identificación {identificacion}.")
        u = Usuario(db.siguiente_id(db.usuarios, "id_usuario"), nombre, apellido, tipo or "Estudiante",
                    identificacion, (correo or "").strip(), (telefono or "").strip(), True)   # RN-02
        db.usuarios.append(u)
        return u

    def cambiar_estado(self, id_usuario, habilitado):
        u = self.obtener(id_usuario)
        if not u:
            raise ReglaNegocioError("El usuario no existe.")
        u.habilitado = bool(habilitado)
        return u
