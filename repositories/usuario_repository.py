from models import Usuario
from . import db
from ._util import patron


def _a_objeto(r):
    return Usuario(r["id_usuario"], r["nombre"], r["apellido"], r["tipo"], r["identificacion"],
                   r["correo"], r["telefono"], bool(r["habilitado"]))


class UsuarioRepository:
    def listar(self, texto=""):
        t = patron(texto)
        with db.sesion() as con:
            filas = con.execute(
                "SELECT * FROM usuario WHERE ? = '' OR instr(minus(nombre || ' ' || apellido || ' ' || "
                "identificacion || ' ' || correo), ?) > 0 ORDER BY id_usuario", (t, t)).fetchall()
        return [_a_objeto(r) for r in filas]

    def obtener(self, id_usuario):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM usuario WHERE id_usuario = ?", (int(id_usuario),)).fetchone()
        return _a_objeto(r) if r else None

    def obtener_por_identificacion(self, identificacion):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM usuario WHERE identificacion = ?", (identificacion,)).fetchone()
        return _a_objeto(r) if r else None

    def guardar(self, u):
        """Inserta el usuario y le asigna su id. Falla (IntegrityError) si la identificación ya existe."""
        with db.sesion() as con:
            cur = con.execute(
                "INSERT INTO usuario (nombre, apellido, tipo, identificacion, correo, telefono, habilitado) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (u.nombre, u.apellido, u.tipo, u.identificacion, u.correo, u.telefono, int(u.habilitado)))
            u.id_usuario = cur.lastrowid
        return u

    def actualizar_estado(self, id_usuario, habilitado):
        with db.sesion() as con:
            con.execute("UPDATE usuario SET habilitado = ? WHERE id_usuario = ?", (int(bool(habilitado)), int(id_usuario)))

    def contar_inhabilitados(self):
        with db.sesion() as con:
            return con.execute("SELECT COUNT(*) FROM usuario WHERE habilitado = 0").fetchone()[0]
