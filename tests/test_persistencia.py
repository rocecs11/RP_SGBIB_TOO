"""Pruebas de persistencia y de la integración con SQLite.

Ejecutar desde la raíz del proyecto:   python -m unittest discover -s tests -v
Cada prueba usa su propia base temporal (variable SGBIB_DB), así que NO toca database/biblioteca.db.
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import date, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from repositories import db, ejemplar_repo, prestamo_repo, usuario_repo   # noqa: E402
from services import (ReglaNegocioError, autenticacion_service, catalogo_service, consulta_service,   # noqa: E402
                      devolucion_service, prestamo_service, usuario_service)
from models import Estado   # noqa: E402


class BaseBD(unittest.TestCase):
    """Cada prueba arranca con una base nueva y vacía en una carpeta temporal."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.tmp.name, "prueba.db")
        os.environ["SGBIB_DB"] = self.ruta
        db.inicializar()

    def tearDown(self):
        os.environ.pop("SGBIB_DB", None)
        self.tmp.cleanup()

    # --- ayudas ---
    def crear_usuario(self, ident="U-1", habilitar=True):
        u = usuario_service.registrar("Ana", "Pérez", "Estudiante", ident, "a@x.com", "7000-0000")
        if not habilitar:
            usuario_service.cambiar_estado(u.id_usuario, False)
        return u

    def crear_ejemplar(self, isbn="978-1", codigo="E-1"):
        l = catalogo_service.registrar_libro("Libro de prueba", "Autor", isbn, "Ed", "2020", "Cat")
        return catalogo_service.registrar_ejemplar(l.id_titulo, codigo, "Estante 1")

    def sql(self, consulta, params=()):
        con = sqlite3.connect(self.ruta)
        try:
            r = con.execute(consulta, params).fetchall()
            con.commit()
            return r
        finally:
            con.close()


class TestPersistencia(BaseBD):
    def test_los_datos_sobreviven_a_un_nuevo_proceso(self):
        """Los datos se guardan en el archivo: otro proceso Python los encuentra (cierre y nueva ejecución)."""
        u = self.crear_usuario("U-PERSIST")
        e = self.crear_ejemplar("978-P", "P-001")
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        codigo = ("import sys; sys.path.insert(0, sys.argv[1])\n"
                  "from services import usuario_service, prestamo_service, catalogo_service\n"
                  "u = usuario_service.listar('U-PERSIST')\n"
                  "p = prestamo_service.listar_activos()\n"
                  "e = catalogo_service.obtener_ejemplar(%d)\n"
                  "print(len(u), len(p), e.estado, p[0].fecha_devolucion_estimada)" % e.id_ejemplar)
        r = subprocess.run([sys.executable, "-I", "-c", codigo, RAIZ], capture_output=True, text=True,
                           env={**os.environ, "SGBIB_DB": self.ruta}, check=True)
        self.assertEqual(r.stdout.split(), ["1", "1", "prestado", str(p.fecha_devolucion_estimada)])

    def test_inicializar_es_repetible_y_no_borra_datos(self):
        self.crear_usuario("U-KEEP")
        db.inicializar()
        self.assertEqual(len(usuario_service.listar()), 1)

    def test_reset_deja_la_base_vacia(self):
        self.crear_usuario("U-1")
        db.inicializar(forzar=True)
        self.assertEqual(usuario_service.listar(), [])

    def test_fechas_se_guardan_como_date(self):
        u = self.crear_usuario()
        e = self.crear_ejemplar()
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        leido = prestamo_service.obtener(p.id_prestamo)
        self.assertEqual(leido.fecha_prestamo, date.today())
        self.assertIsInstance(leido.fecha_devolucion_estimada, date)
        self.assertEqual(catalogo_service.obtener_ejemplar(e.id_ejemplar).fecha_adquisicion, date.today())


class TestReglasConPersistencia(BaseBD):
    # US-01
    def test_usuario_nace_habilitado_y_obligatorios(self):
        self.assertTrue(self.crear_usuario().habilitado)
        with self.assertRaises(ReglaNegocioError):
            usuario_service.registrar("", "X", "Estudiante", "U-9")
        with self.assertRaises(ReglaNegocioError):
            usuario_service.registrar("A", "B", "Estudiante", "  ")

    def test_identificacion_duplicada_rechazada_sin_importar_mayusculas(self):
        self.crear_usuario("U-77")
        with self.assertRaisesRegex(ReglaNegocioError, "Ya existe un usuario"):
            usuario_service.registrar("Otro", "Nombre", "Docente", "u-77")
        self.assertEqual(len(usuario_service.listar()), 1)

    def test_la_base_tambien_impide_duplicados(self):
        """Aunque el servicio fallara, SQLite rechaza identificación, ISBN y código repetidos."""
        self.crear_usuario("U-1")
        e = self.crear_ejemplar("978-X", "C-1")
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO usuario (nombre, apellido, identificacion) VALUES ('a','b','u-1')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO libro (isbn, titulo, autor) VALUES ('978-X','t','a')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO ejemplar (id_titulo, codigo) VALUES (?, 'c-1')", (e.id_titulo,))

    # US-02
    def test_titulo_y_ejemplar_validaciones(self):
        with self.assertRaises(ReglaNegocioError):
            catalogo_service.registrar_libro("", "A", "1")
        with self.assertRaisesRegex(ReglaNegocioError, "número"):
            catalogo_service.registrar_libro("T", "A", "978-A", anio_publicacion="abc")
        e = self.crear_ejemplar("978-B", "B-1")
        self.assertEqual(e.estado, Estado.DISPONIBLE)
        with self.assertRaisesRegex(ReglaNegocioError, "código"):
            catalogo_service.registrar_ejemplar(e.id_titulo, "b-1")
        with self.assertRaisesRegex(ReglaNegocioError, "no existe"):
            catalogo_service.registrar_ejemplar(999, "Z-1")

    # US-04 / US-05
    def test_prestamo_valido_fechas_y_estado(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        self.assertEqual(p.fecha_devolucion_estimada - p.fecha_prestamo, timedelta(days=7))
        self.assertEqual(catalogo_service.obtener_ejemplar(e.id_ejemplar).estado, Estado.PRESTADO)

    def test_usuario_inhabilitado_no_puede_prestar_y_nada_cambia(self):
        u, e = self.crear_usuario(habilitar=False), self.crear_ejemplar()
        with self.assertRaisesRegex(ReglaNegocioError, "inhabilitado"):
            prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        self.assertEqual(prestamo_service.listar_activos(), [])
        self.assertEqual(catalogo_service.obtener_ejemplar(e.id_ejemplar).estado, Estado.DISPONIBLE)

    def test_entradas_invalidas(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        for uid, eid, texto in [("", e.id_ejemplar, "usuario"), ("abc", e.id_ejemplar, "usuario"),
                                (u.id_usuario, "", "ejemplar"), (u.id_usuario, 9999, "ejemplar")]:
            with self.assertRaisesRegex(ReglaNegocioError, texto):
                prestamo_service.registrar(uid, eid)

    def test_ejemplar_fuera_de_servicio_no_se_presta(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        catalogo_service.cambiar_estado_ejemplar(e.id_ejemplar, Estado.FUERA_DE_SERVICIO, "daño")
        with self.assertRaisesRegex(ReglaNegocioError, "no está disponible"):
            prestamo_service.registrar(u.id_usuario, e.id_ejemplar)

    # US-06
    def test_prestamo_duplicado_rechazado_sin_afectar_el_original(self):
        u1, u2, e = self.crear_usuario("U-1"), self.crear_usuario("U-2"), self.crear_ejemplar()
        original = prestamo_service.registrar(u1.id_usuario, e.id_ejemplar)
        with self.assertRaisesRegex(ReglaNegocioError, "ya tiene un préstamo activo"):
            prestamo_service.registrar(u2.id_usuario, e.id_ejemplar)
        activos = prestamo_service.listar_activos()
        self.assertEqual([(p.id_prestamo, p.id_usuario) for p in activos], [(original.id_prestamo, u1.id_usuario)])

    def test_solicitudes_simultaneas_crean_un_solo_prestamo(self):
        usuarios = [self.crear_usuario(f"U-{i}") for i in range(8)]
        e = self.crear_ejemplar()
        resultados, barrera = [], threading.Barrier(len(usuarios))

        def pedir(u):
            barrera.wait()
            try:
                prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
                resultados.append("ok")
            except ReglaNegocioError:
                resultados.append("rechazado")

        hilos = [threading.Thread(target=pedir, args=(u,)) for u in usuarios]
        [h.start() for h in hilos]
        [h.join() for h in hilos]
        self.assertEqual(resultados.count("ok"), 1)
        self.assertEqual(resultados.count("rechazado"), 7)
        self.assertEqual(self.sql("SELECT COUNT(*) FROM prestamo WHERE estado='activo'")[0][0], 1)

    def test_indice_unico_impide_dos_activos_aunque_se_salte_el_servicio(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO prestamo (id_usuario, id_ejemplar, fecha_prestamo, fecha_devolucion_estimada, estado) "
                     "VALUES (?, ?, '2026-01-01', '2026-01-08', 'activo')", (u.id_usuario, e.id_ejemplar))

    def test_transaccion_revierte_todo_si_hay_error(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        with self.assertRaises(RuntimeError):
            with db.transaccion():
                ejemplar_repo.actualizar_estado(e.id_ejemplar, Estado.PRESTADO)
                raise RuntimeError("fallo simulado")
        self.assertEqual(ejemplar_repo.obtener(e.id_ejemplar).estado, Estado.DISPONIBLE)

    # US-07 / US-08
    def test_devolucion_a_tiempo_libera_ejemplar_sin_retraso(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        d, retraso = devolucion_service.registrar(p.id_prestamo, "Sin novedades")
        self.assertIsNone(retraso)
        self.assertEqual(d.fecha_devolucion, date.today())
        self.assertEqual(prestamo_service.obtener(p.id_prestamo).estado, Estado.DEVUELTO)
        self.assertEqual(catalogo_service.obtener_ejemplar(e.id_ejemplar).estado, Estado.DISPONIBLE)
        self.assertIsNone(devolucion_service.retraso_de(p.id_prestamo))

    def test_devolucion_tardia_registra_retraso_asociado_al_prestamo(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        vencida = (date.today() - timedelta(days=5)).isoformat()
        self.sql("UPDATE prestamo SET fecha_devolucion_estimada = ? WHERE id_prestamo = ?", (vencida, p.id_prestamo))
        _, retraso = devolucion_service.registrar(p.id_prestamo)
        self.assertEqual((retraso.id_prestamo, retraso.dias_retraso), (p.id_prestamo, 5))
        guardado = devolucion_service.retraso_de(p.id_prestamo)
        self.assertEqual(guardado.dias_retraso, 5)
        self.assertEqual(guardado.estado, "registrado")

    def test_devolucion_invalida_o_repetida(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        devolucion_service.registrar(p.id_prestamo)
        for dato in (p.id_prestamo, 9999, "", "abc"):
            with self.assertRaisesRegex(ReglaNegocioError, "No existe un préstamo activo"):
                devolucion_service.registrar(dato)
        self.assertEqual(self.sql("SELECT COUNT(*) FROM devolucion")[0][0], 1)

    def test_devolucion_fuera_de_servicio_exige_motivo_y_no_guarda_nada_si_falla(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        p = prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        with self.assertRaisesRegex(ReglaNegocioError, "motivo"):
            devolucion_service.registrar(p.id_prestamo, "", True, None)
        self.assertEqual(prestamo_service.obtener(p.id_prestamo).estado, Estado.ACTIVO)
        self.assertEqual(self.sql("SELECT COUNT(*) FROM devolucion")[0][0], 0)
        devolucion_service.registrar(p.id_prestamo, "Páginas rotas", True, "daño")
        ej = catalogo_service.obtener_ejemplar(e.id_ejemplar)
        self.assertEqual((ej.estado, ej.motivo), (Estado.FUERA_DE_SERVICIO, "daño"))

    # US-09
    def test_fuera_de_servicio_y_reactivacion(self):
        u, e = self.crear_usuario(), self.crear_ejemplar()
        with self.assertRaisesRegex(ReglaNegocioError, "motivo"):
            catalogo_service.cambiar_estado_ejemplar(e.id_ejemplar, Estado.FUERA_DE_SERVICIO)
        catalogo_service.cambiar_estado_ejemplar(e.id_ejemplar, Estado.FUERA_DE_SERVICIO, "mantenimiento")
        self.assertEqual(consulta_service.resumen()["fuera_servicio"], 1)
        self.assertEqual(consulta_service.resumen()["disponibles"], 0)
        catalogo_service.cambiar_estado_ejemplar(e.id_ejemplar, Estado.DISPONIBLE)
        ej = catalogo_service.obtener_ejemplar(e.id_ejemplar)
        self.assertEqual((ej.estado, ej.motivo), (Estado.DISPONIBLE, None))
        prestamo_service.registrar(u.id_usuario, e.id_ejemplar)
        with self.assertRaisesRegex(ReglaNegocioError, "prestado"):
            catalogo_service.cambiar_estado_ejemplar(e.id_ejemplar, Estado.FUERA_DE_SERVICIO, "daño")

    def test_la_base_rechaza_motivo_sin_estado_fuera_de_servicio(self):
        e = self.crear_ejemplar()
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("UPDATE ejemplar SET motivo = 'daño' WHERE id_ejemplar = ?", (e.id_ejemplar,))


class TestConsultas(BaseBD):
    def setUp(self):
        super().setUp()
        self.u1 = usuario_service.registrar("María", "Ñandú", "Docente", "D-1")
        self.u2 = self.crear_usuario("U-2")
        l = catalogo_service.registrar_libro("Cien años de soledad", "Gabriel García Márquez", "978-5", "Alfaguara", "1967", "Novela")
        self.e1 = catalogo_service.registrar_ejemplar(l.id_titulo, "CS-001")
        self.e2 = catalogo_service.registrar_ejemplar(l.id_titulo, "CS-002")
        self.p1 = prestamo_service.registrar(self.u1.id_usuario, self.e1.id_ejemplar)
        self.p2 = prestamo_service.registrar(self.u2.id_usuario, self.e2.id_ejemplar)
        devolucion_service.registrar(self.p2.id_prestamo)

    def test_busqueda_por_titulo_autor_isbn_sin_mayusculas_ni_tildes_exactas(self):
        for q in ("SOLEDAD", "garcía", "978-5", "márquez"):
            self.assertEqual(len(consulta_service.disponibilidad(q)), 1, q)
        self.assertEqual(consulta_service.disponibilidad("no existe"), [])
        libro, ejemplares = consulta_service.disponibilidad("")[0]
        self.assertEqual(sorted(e.estado for e in ejemplares), [Estado.DISPONIBLE, Estado.PRESTADO])

    def test_poseedor_por_codigo(self):
        e, p = consulta_service.poseedor("cs-001")
        self.assertEqual((e.codigo, p.id_usuario), ("CS-001", self.u1.id_usuario))
        e, p = consulta_service.poseedor("CS-002")
        self.assertIsNone(p)                       # devuelto: ya no lo posee nadie
        self.assertEqual(consulta_service.poseedor("XX-999"), (None, None))

    def test_prestamos_activos_con_filtro(self):
        self.assertEqual(len(prestamo_service.listar_activos()), 1)
        self.assertEqual(len(prestamo_service.listar_activos("ÑANDÚ")), 1)      # mayúscula con tilde y Ñ
        self.assertEqual(len(prestamo_service.listar_activos("CS-001")), 1)
        self.assertEqual(prestamo_service.listar_activos("U-2"), [])           # su préstamo ya está cerrado

    def test_historial_incluye_activos_y_cerrados(self):
        self.assertEqual(len(consulta_service.historial("usuario", "")), 2)
        self.assertEqual(len(consulta_service.historial("usuario", "D-1")), 1)
        self.assertEqual(len(consulta_service.historial("titulo", "soledad")), 2)
        self.assertEqual(len(consulta_service.historial("ejemplar", "cs-002")), 1)
        self.assertEqual(consulta_service.historial("ejemplar", "nada"), [])

    def test_resumen(self):
        self.assertEqual(consulta_service.resumen(),
                         {"disponibles": 1, "prestados": 1, "fuera_servicio": 0, "activos": 1, "con_retraso": 0, "inhabilitados": 0})


class TestAutenticacionYWeb(BaseBD):
    def setUp(self):
        super().setUp()
        from database.init_db import asegurar_admin
        os.environ.pop("SGBIB_ADMIN_PASSWORD", None)
        asegurar_admin()
        from app import create_app
        self.app = create_app()
        self.app.testing = True
        self.c = self.app.test_client()

    def test_contrasena_guardada_cifrada(self):
        guardado = self.sql("SELECT contrasena FROM bibliotecario WHERE usuario='admin'")[0][0]
        self.assertNotIn("admin123", guardado)
        self.assertTrue(guardado.startswith(("scrypt:", "pbkdf2:")))

    def test_login(self):
        self.assertIsNone(autenticacion_service.iniciar_sesion("admin", "mala"))
        self.assertIsNone(autenticacion_service.iniciar_sesion("", ""))
        self.assertIsNotNone(autenticacion_service.iniciar_sesion("ADMIN", "admin123"))

    def test_rutas_protegidas(self):
        r = self.c.get("/usuarios/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])

    def test_flujo_completo_por_la_web(self):
        c = self.c
        r = c.post("/login", data={"usuario": "admin", "contrasena": "mala"})
        self.assertIn("incorrectos".encode(), r.data)
        self.assertEqual(c.post("/login", data={"usuario": "admin", "contrasena": "admin123"}).status_code, 302)
        # usuario
        c.post("/usuarios/nuevo", data={"nombre": "Eva", "apellido": "Luna", "tipo": "Docente", "identificacion": "D-9"})
        r = c.post("/usuarios/nuevo", data={"nombre": "Eva", "apellido": "Luna", "tipo": "Docente", "identificacion": "D-9"},
                   follow_redirects=True)
        self.assertIn("Ya existe un usuario".encode(), r.data)
        # catálogo
        r = c.post("/catalogo/libros/nuevo", data={"titulo": "Libro", "autor": "Aut", "isbn": "978-9"}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        c.post("/catalogo/libros/1/ejemplares/nuevo", data={"codigo": "L-1", "ubicacion": "A"})
        # préstamo y duplicado
        r = c.post("/prestamos/nuevo", data={"id_usuario": "1", "id_ejemplar": "1"}, follow_redirects=True)
        self.assertIn("Préstamo registrado".encode(), r.data)
        r = c.post("/prestamos/nuevo", data={"id_usuario": "1", "id_ejemplar": "1"}, follow_redirects=True)
        self.assertIn("ya tiene un préstamo activo".encode(), r.data)
        # consultas
        self.assertIn(b"Eva", c.get("/prestamos").data)
        self.assertIn(b"Eva", c.get("/consultas/poseedor?codigo=L-1").data)
        self.assertEqual(c.get("/consultas/historial?tipo=ejemplar&q=L-1").status_code, 200)
        self.assertEqual(c.get("/").status_code, 200)
        # devolución
        r = c.post("/prestamos/1/devolver", data={"observaciones": "ok"}, follow_redirects=True)
        self.assertIn("Devolución registrada".encode(), r.data)
        self.assertEqual(self.sql("SELECT estado FROM ejemplar")[0][0], "disponible")
        # inhabilitar y volver a intentar
        c.post("/usuarios/1/estado", data={"habilitado": "0"})
        r = c.post("/prestamos/nuevo", data={"id_usuario": "1", "id_ejemplar": "1"}, follow_redirects=True)
        self.assertIn(b"inhabilitado", r.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
