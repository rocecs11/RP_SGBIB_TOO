from models import Bibliotecario
from . import db


def _a_objeto(r):
    return Bibliotecario(r["id_bibliotecario"], r["nombre"], r["usuario"], r["contrasena"])   # contrasena = hash


class BibliotecarioRepository:
    def obtener_por_usuario(self, usuario):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM bibliotecario WHERE usuario = ?", (usuario,)).fetchone()
        return _a_objeto(r) if r else None

    def guardar(self, b):
        """Inserta un bibliotecario. `b.contrasena` debe venir ya cifrada."""
        with db.sesion() as con:
            cur = con.execute("INSERT INTO bibliotecario (nombre, usuario, contrasena) VALUES (?, ?, ?)",
                              (b.nombre, b.usuario, b.contrasena))
            b.id_bibliotecario = cur.lastrowid
        return b

    def contar(self):
        with db.sesion() as con:
            return con.execute("SELECT COUNT(*) FROM bibliotecario").fetchone()[0]
