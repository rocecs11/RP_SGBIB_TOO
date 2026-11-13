"""Prepara la base de datos SQLite del SGBIB.

Uso (desde la carpeta del proyecto):
    python database/init_db.py              crea biblioteca.db y las tablas si no existen (no borra datos)
    python database/init_db.py --demo       además carga datos de ejemplo (solo si la base está vacía)
    python database/init_db.py --reset      BORRA biblioteca.db y la crea de nuevo (vacía)
    python database/init_db.py --reset --demo    base nueva con datos de ejemplo

En Windows use `py` en lugar de `python`.
Siempre se crea el bibliotecario de prueba `admin`; su contraseña se guarda cifrada. Por defecto es `admin123`
(solo para pruebas) y puede cambiarse con la variable de entorno SGBIB_ADMIN_PASSWORD antes de ejecutar el script.
No se guardan contraseñas reales en el código ni en la base entregada.
"""
import argparse
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # raíz del proyecto

from werkzeug.security import generate_password_hash   # noqa: E402

from models import Bibliotecario, Usuario, Libro, Ejemplar, Prestamo, Devolucion, Retraso, Estado   # noqa: E402
from repositories import (db, bibliotecario_repo, usuario_repo, libro_repo, ejemplar_repo,   # noqa: E402
                          prestamo_repo, devolucion_repo)

CONTRASENA_PRUEBA = "admin123"


def asegurar_admin():
    """Crea el bibliotecario de prueba si todavía no hay ninguno."""
    if bibliotecario_repo.contar() == 0:
        clave = os.environ.get("SGBIB_ADMIN_PASSWORD") or CONTRASENA_PRUEBA
        bibliotecario_repo.guardar(Bibliotecario(None, "Marta Hernández", "admin", generate_password_hash(clave)))
        return True
    return False


def cargar_demo():
    """Datos de ejemplo (fechas relativas a hoy). Solo se cargan si no hay usuarios ni títulos."""
    if usuario_repo.listar() or libro_repo.listar():
        return False
    hoy = date.today()
    with db.transaccion():
        for n, a, t, i, c, tel, h in [
            ("Carlos", "Mejía", "Estudiante", "U-2201", "carlos.mejia@correo.com", "7000-1111", True),
            ("Ana", "Ramírez", "Estudiante", "U-2202", "ana.ramirez@correo.com", "7000-2222", True),
            ("Luis", "Portillo", "Docente", "D-0101", "luis.portillo@correo.com", "7000-3333", True),
            ("Sofía", "Cruz", "Estudiante", "U-2204", "sofia.cruz@correo.com", "7000-4444", False),
            ("Jorge", "Alas", "Externo", "E-0501", "jorge.alas@correo.com", "7000-5555", True)]:
            usuario_repo.guardar(Usuario(None, n, a, t, i, c, tel, h))
        for isbn, titulo, autor, ed, anio, cat in [
            ("978-0132350884", "Clean Code", "Robert C. Martin", "Prentice Hall", 2008, "Programación"),
            ("978-0201633610", "Design Patterns", "Erich Gamma", "Addison-Wesley", 1994, "Programación"),
            ("978-0134494166", "Clean Architecture", "Robert C. Martin", "Prentice Hall", 2017, "Arquitectura"),
            ("978-0321125217", "Domain-Driven Design", "Eric Evans", "Addison-Wesley", 2003, "Arquitectura"),
            ("978-8420471839", "Cien años de soledad", "Gabriel García Márquez", "Alfaguara", 1967, "Novela"),
            ("978-0136042595", "Ingeniería de Software", "Ian Sommerville", "Pearson", 2011, "Ingeniería")]:
            libro_repo.guardar(Libro(None, isbn, titulo, autor, ed, anio, cat))
        for id_t, cod, dias, ubic, est, mot in [
            (1, "CC-001", 900, "Estante A1", Estado.DISPONIBLE, None), (1, "CC-002", 900, "Estante A1", Estado.DISPONIBLE, None),
            (2, "DP-001", 700, "Estante A2", Estado.DISPONIBLE, None), (2, "DP-002", 700, "Estante A2", Estado.FUERA_DE_SERVICIO, "daño"),
            (3, "CA-001", 400, "Estante B1", Estado.DISPONIBLE, None), (4, "DD-001", 380, "Estante B1", Estado.DISPONIBLE, None),
            (4, "DD-002", 380, "Estante B1", Estado.DISPONIBLE, None), (5, "CS-001", 1500, "Estante C3", Estado.DISPONIBLE, None),
            (5, "CS-002", 1500, "Estante C3", Estado.FUERA_DE_SERVICIO, "mantenimiento"),
            (6, "IS-001", 200, "Estante D2", Estado.DISPONIBLE, None), (6, "IS-002", 200, "Estante D2", Estado.DISPONIBLE, None)]:
            ejemplar_repo.guardar(Ejemplar(None, id_t, cod, hoy - timedelta(days=dias), ubic, est, mot))

        def prestamo(id_u, id_e, atras, plazo=7, estado=Estado.DEVUELTO):
            p = Prestamo(None, id_u, id_e, hoy - timedelta(days=atras), hoy - timedelta(days=atras - plazo), estado)
            return prestamo_repo.guardar(p)

        # Préstamos activos: uno vigente, uno vencido (retraso en curso) y otro vigente
        for id_u, id_e, atras in [(1, 1, 3), (2, 5, 12), (3, 8, 1)]:
            prestamo(id_u, id_e, atras, estado=Estado.ACTIVO)
            ejemplar_repo.actualizar_estado(id_e, Estado.PRESTADO)
        # Historial: devuelto a tiempo, devuelto con retraso (3 días) y varios recientes a tiempo
        p = prestamo(2, 3, 40)
        devolucion_repo.guardar(Devolucion(None, p.id_prestamo, hoy - timedelta(days=33), "Sin novedades"))
        p = prestamo(1, 6, 30)
        devolucion_repo.guardar(Devolucion(None, p.id_prestamo, hoy - timedelta(days=20), "Devuelto con retraso"))
        devolucion_repo.guardar_retraso(Retraso(None, p.id_prestamo, 3))
        for id_u, id_e, atras, dev in [(3, 7, 6, 4), (5, 10, 5, 2), (1, 11, 2, 1), (2, 2, 4, 3), (3, 6, 1, 0)]:
            p = prestamo(id_u, id_e, atras)
            devolucion_repo.guardar(Devolucion(None, p.id_prestamo, hoy - timedelta(days=dev), ""))
    return True


def main():
    ap = argparse.ArgumentParser(description="Prepara la base de datos SQLite del SGBIB.")
    ap.add_argument("--reset", action="store_true", help="borra la base de datos y la crea de nuevo")
    ap.add_argument("--demo", action="store_true", help="carga datos de ejemplo si la base está vacía")
    a = ap.parse_args()
    db.inicializar(forzar=a.reset)
    print(f"Base de datos lista: {db.ruta_bd()}")
    if asegurar_admin():
        print("Bibliotecario de prueba creado: usuario 'admin' (contraseña de prueba 'admin123' o SGBIB_ADMIN_PASSWORD).")
    if a.demo:
        print("Datos de ejemplo cargados." if cargar_demo() else "Datos de ejemplo NO cargados: la base ya tiene información.")


if __name__ == "__main__":
    main()
