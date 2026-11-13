from models import Libro
from . import db
from ._util import patron


def _a_objeto(r):
    return Libro(r["id_titulo"], r["isbn"], r["titulo"], r["autor"], r["editorial"],
                 r["anio_publicacion"], r["categoria"])


class LibroRepository:
    def listar(self, texto=""):
        t = patron(texto)
        with db.sesion() as con:
            filas = con.execute(
                "SELECT * FROM libro WHERE ? = '' OR instr(minus(titulo || ' ' || autor || ' ' || isbn), ?) > 0 "
                "ORDER BY id_titulo", (t, t)).fetchall()
        return [_a_objeto(r) for r in filas]

    def obtener(self, id_titulo):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM libro WHERE id_titulo = ?", (int(id_titulo),)).fetchone()
        return _a_objeto(r) if r else None

    def obtener_por_isbn(self, isbn):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM libro WHERE isbn = ?", (isbn,)).fetchone()
        return _a_objeto(r) if r else None

    def guardar(self, l):
        with db.sesion() as con:
            cur = con.execute(
                "INSERT INTO libro (isbn, titulo, autor, editorial, anio_publicacion, categoria) VALUES (?, ?, ?, ?, ?, ?)",
                (l.isbn, l.titulo, l.autor, l.editorial, l.anio_publicacion, l.categoria))
            l.id_titulo = cur.lastrowid
        return l
