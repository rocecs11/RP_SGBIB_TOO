"""DATOS DE PRUEBA EN MEMORIA (temporal).
Sustituye a los repositorios del compañero mientras se integra el código real.
Se borra al integrar: los servicios reales leerán/escribirán en SQLite."""
import threading
from datetime import date, timedelta
from models import Bibliotecario, Usuario, Libro, Ejemplar, Prestamo, Devolucion, Retraso, Estado

candado = threading.Lock()   # evita dos préstamos simultáneos del mismo ejemplar (US-06)
hoy = date.today()

bibliotecarios = [Bibliotecario(1, "Marta Hernández", "admin", "admin123")]

usuarios = [
    Usuario(1, "Carlos", "Mejía", "Estudiante", "U-2201", "carlos.mejia@correo.com", "7000-1111", True),
    Usuario(2, "Ana", "Ramírez", "Estudiante", "U-2202", "ana.ramirez@correo.com", "7000-2222", True),
    Usuario(3, "Luis", "Portillo", "Docente", "D-0101", "luis.portillo@correo.com", "7000-3333", True),
    Usuario(4, "Sofía", "Cruz", "Estudiante", "U-2204", "sofia.cruz@correo.com", "7000-4444", False),
    Usuario(5, "Jorge", "Alas", "Externo", "E-0501", "jorge.alas@correo.com", "7000-5555", True),
]

libros = [
    Libro(1, "978-0132350884", "Clean Code", "Robert C. Martin", "Prentice Hall", 2008, "Programación"),
    Libro(2, "978-0201633610", "Design Patterns", "Erich Gamma", "Addison-Wesley", 1994, "Programación"),
    Libro(3, "978-0134494166", "Clean Architecture", "Robert C. Martin", "Prentice Hall", 2017, "Arquitectura"),
    Libro(4, "978-0321125217", "Domain-Driven Design", "Eric Evans", "Addison-Wesley", 2003, "Arquitectura"),
    Libro(5, "978-8420471839", "Cien años de soledad", "Gabriel García Márquez", "Alfaguara", 1967, "Novela"),
    Libro(6, "978-0136042595", "Ingeniería de Software", "Ian Sommerville", "Pearson", 2011, "Ingeniería"),
]

ejemplares = [
    Ejemplar(1, 1, "CC-001", hoy - timedelta(days=900), "Estante A1"),
    Ejemplar(2, 1, "CC-002", hoy - timedelta(days=900), "Estante A1"),
    Ejemplar(3, 2, "DP-001", hoy - timedelta(days=700), "Estante A2"),
    Ejemplar(4, 2, "DP-002", hoy - timedelta(days=700), "Estante A2", Estado.FUERA_DE_SERVICIO, "daño"),
    Ejemplar(5, 3, "CA-001", hoy - timedelta(days=400), "Estante B1"),
    Ejemplar(6, 4, "DD-001", hoy - timedelta(days=380), "Estante B1"),
    Ejemplar(7, 4, "DD-002", hoy - timedelta(days=380), "Estante B1"),
    Ejemplar(8, 5, "CS-001", hoy - timedelta(days=1500), "Estante C3"),
    Ejemplar(9, 5, "CS-002", hoy - timedelta(days=1500), "Estante C3", Estado.FUERA_DE_SERVICIO, "mantenimiento"),
    Ejemplar(10, 6, "IS-001", hoy - timedelta(days=200), "Estante D2"),
    Ejemplar(11, 6, "IS-002", hoy - timedelta(days=200), "Estante D2"),
]

prestamos = []
devoluciones = []
retrasos = []


def _prestamo_activo(id_u, id_e, dias_atras, plazo=7):
    pr = Prestamo(len(prestamos) + 1, id_u, id_e, hoy - timedelta(days=dias_atras),
                  hoy - timedelta(days=dias_atras) + timedelta(days=plazo))
    prestamos.append(pr)
    next(e for e in ejemplares if e.id_ejemplar == id_e).estado = Estado.PRESTADO


_prestamo_activo(1, 1, 3)    # vigente
_prestamo_activo(2, 5, 12)   # con retraso (vencido hace 5 días)
_prestamo_activo(3, 8, 1)    # vigente

# Historial: dos préstamos ya devueltos (uno con retraso)
p = Prestamo(4, 2, 3, hoy - timedelta(days=40), hoy - timedelta(days=33), Estado.DEVUELTO)
prestamos.append(p)
devoluciones.append(Devolucion(1, 4, hoy - timedelta(days=33), "Sin novedades"))
p = Prestamo(5, 1, 6, hoy - timedelta(days=30), hoy - timedelta(days=23), Estado.DEVUELTO)
prestamos.append(p)
devoluciones.append(Devolucion(2, 5, hoy - timedelta(days=20), "Devuelto con retraso"))
retrasos.append(Retraso(1, 5, 3))


# Más historial reciente (todos devueltos a tiempo) para los gráficos del panel
for id_p, id_u, id_e, atras, dev in [(6, 3, 7, 6, 4), (7, 5, 10, 5, 2), (8, 1, 11, 2, 1), (9, 2, 2, 4, 3), (10, 3, 6, 1, 0)]:
    prestamos.append(Prestamo(id_p, id_u, id_e, hoy - timedelta(days=atras), hoy - timedelta(days=atras) + timedelta(days=7), Estado.DEVUELTO))
    devoluciones.append(Devolucion(len(devoluciones) + 1, id_p, hoy - timedelta(days=dev), ""))


def siguiente_id(lista, atributo):
    return max((getattr(x, atributo) for x in lista), default=0) + 1
