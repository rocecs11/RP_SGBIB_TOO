from models import Prestamo, Estado
from . import db
from ._util import a_fecha, de_fecha, patron

# Texto sobre el que se filtra cada tipo de consulta (US-11, US-12)
_CAMPOS = {
    "todo":     "u.nombre || ' ' || u.apellido || ' ' || u.identificacion || ' ' || e.codigo || ' ' || l.titulo",
    "usuario":  "u.nombre || ' ' || u.apellido || ' ' || u.identificacion",
    "titulo":   "l.titulo || ' ' || l.autor",
    "ejemplar": "e.codigo",
}

_BASE = ("SELECT p.* FROM prestamo p JOIN usuario u ON u.id_usuario = p.id_usuario "
         "JOIN ejemplar e ON e.id_ejemplar = p.id_ejemplar JOIN libro l ON l.id_titulo = e.id_titulo ")


def _a_objeto(r):
    return Prestamo(r["id_prestamo"], r["id_usuario"], r["id_ejemplar"], a_fecha(r["fecha_prestamo"]),
                    a_fecha(r["fecha_devolucion_estimada"]), r["estado"])


class PrestamoRepository:
    def guardar(self, p):
        """Inserta el préstamo. Si el ejemplar ya tiene uno activo, SQLite lanza IntegrityError (RN-10)."""
        with db.sesion() as con:
            cur = con.execute(
                "INSERT INTO prestamo (id_usuario, id_ejemplar, fecha_prestamo, fecha_devolucion_estimada, estado) "
                "VALUES (?, ?, ?, ?, ?)",
                (p.id_usuario, p.id_ejemplar, de_fecha(p.fecha_prestamo), de_fecha(p.fecha_devolucion_estimada), p.estado))
            p.id_prestamo = cur.lastrowid
        return p

    def obtener(self, id_prestamo):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM prestamo WHERE id_prestamo = ?", (int(id_prestamo),)).fetchone()
        return _a_objeto(r) if r else None

    def obtener_activo_de_ejemplar(self, id_ejemplar):
        with db.sesion() as con:
            r = con.execute("SELECT * FROM prestamo WHERE id_ejemplar = ? AND estado = ?",
                            (int(id_ejemplar), Estado.ACTIVO)).fetchone()
        return _a_objeto(r) if r else None

    def listar_activos(self, texto=""):
        """Préstamos activos; `texto` filtra por usuario, ejemplar o título (US-11)."""
        t = patron(texto)
        with db.sesion() as con:
            filas = con.execute(_BASE + f"WHERE p.estado = ? AND (? = '' OR instr(minus({_CAMPOS['todo']}), ?) > 0) "
                                        "ORDER BY p.fecha_devolucion_estimada, p.id_prestamo",
                                (Estado.ACTIVO, t, t)).fetchall()
        return [_a_objeto(r) for r in filas]

    def historial(self, tipo="usuario", texto=""):
        """Préstamos activos y cerrados, del más reciente al más antiguo (US-12)."""
        t = patron(texto)
        campo = _CAMPOS.get(tipo)
        if campo is None:                     # tipo desconocido: no coincide con nada (igual que la demo)
            return [] if t else self.historial("todo", "")
        with db.sesion() as con:
            filas = con.execute(_BASE + f"WHERE (? = '' OR instr(minus({campo}), ?) > 0) "
                                        "ORDER BY p.fecha_prestamo DESC, p.id_prestamo DESC", (t, t)).fetchall()
        return [_a_objeto(r) for r in filas]

    def marcar_devuelto(self, id_prestamo):
        with db.sesion() as con:
            con.execute("UPDATE prestamo SET estado = ? WHERE id_prestamo = ?", (Estado.DEVUELTO, int(id_prestamo)))
