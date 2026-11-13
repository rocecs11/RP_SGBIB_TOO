"""Persistencia de devoluciones y de los retrasos que generan (la devolución origina el retraso)."""
from models import Devolucion, Retraso
from . import db
from ._util import a_fecha, de_fecha


def _dev(r):
    return Devolucion(r["id_devolucion"], r["id_prestamo"], a_fecha(r["fecha_devolucion"]), r["observaciones"])


def _ret(r):
    return Retraso(r["id_retraso"], r["id_prestamo"], r["dias_retraso"], r["estado"])


class DevolucionRepository:
    def guardar(self, d):
        with db.sesion() as con:
            cur = con.execute("INSERT INTO devolucion (id_prestamo, fecha_devolucion, observaciones) VALUES (?, ?, ?)",
                              (d.id_prestamo, de_fecha(d.fecha_devolucion), d.observaciones))
            d.id_devolucion = cur.lastrowid
        return d

    def obtener_de_prestamo(self, id_prestamo):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM devolucion WHERE id_prestamo = ?", (int(id_prestamo),)).fetchone()
        return _dev(r) if r else None

    def guardar_retraso(self, r):
        with db.sesion() as con:
            cur = con.execute("INSERT INTO retraso (id_prestamo, dias_retraso, estado) VALUES (?, ?, ?)",
                              (r.id_prestamo, r.dias_retraso, r.estado))
            r.id_retraso = cur.lastrowid
        return r

    def retraso_de_prestamo(self, id_prestamo):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM retraso WHERE id_prestamo = ?", (int(id_prestamo),)).fetchone()
        return _ret(r) if r else None
