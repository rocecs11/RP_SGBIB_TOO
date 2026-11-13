from models import Ejemplar
from . import db
from ._util import a_fecha, de_fecha


def _a_objeto(r):
    return Ejemplar(r["id_ejemplar"], r["id_titulo"], r["codigo"], a_fecha(r["fecha_adquisicion"]),
                    r["ubicacion"], r["estado"], r["motivo"])


class EjemplarRepository:
    def listar(self, id_titulo=None):
        with db.sesion() as con:
            if id_titulo is None:
                filas = con.execute("SELECT * FROM ejemplar ORDER BY id_ejemplar").fetchall()
            else:
                filas = con.execute("SELECT * FROM ejemplar WHERE id_titulo = ? ORDER BY id_ejemplar",
                                    (int(id_titulo),)).fetchall()
        return [_a_objeto(r) for r in filas]

    def obtener(self, id_ejemplar):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM ejemplar WHERE id_ejemplar = ?", (int(id_ejemplar),)).fetchone()
        return _a_objeto(r) if r else None

    def obtener_por_codigo(self, codigo):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM ejemplar WHERE codigo = ?", ((codigo or "").strip(),)).fetchone()
        return _a_objeto(r) if r else None

    def guardar(self, e):
        with db.sesion() as con:
            cur = con.execute(
                "INSERT INTO ejemplar (id_titulo, codigo, fecha_adquisicion, ubicacion, estado, motivo) VALUES (?, ?, ?, ?, ?, ?)",
                (e.id_titulo, e.codigo, de_fecha(e.fecha_adquisicion), e.ubicacion, e.estado, e.motivo))
            e.id_ejemplar = cur.lastrowid
        return e

    def actualizar_estado(self, id_ejemplar, estado, motivo=None):
        with db.sesion() as con:
            con.execute("UPDATE ejemplar SET estado = ?, motivo = ? WHERE id_ejemplar = ?",
                        (estado, motivo, int(id_ejemplar)))

    def contar_por_estado(self):
        """Devuelve {estado: cantidad} para el resumen del panel."""
        with db.sesion() as con:
            return {r["estado"]: r["n"] for r in con.execute("SELECT estado, COUNT(*) AS n FROM ejemplar GROUP BY estado")}
