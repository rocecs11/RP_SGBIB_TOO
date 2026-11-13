from werkzeug.security import check_password_hash
from repositories import bibliotecario_repo


class AutenticacionService:
    """Valida el acceso del bibliotecario. La contraseña se guarda cifrada (hash) en la base de datos."""

    def iniciar_sesion(self, usuario, contrasena):
        b = bibliotecario_repo.obtener_por_usuario((usuario or "").strip())
        if b and check_password_hash(b.contrasena, contrasena or ""):
            return b
        return None
