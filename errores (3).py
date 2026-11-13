"""Utilidades de la capa de interfaz: protección de rutas y armado de filas para las tablas.
Si cambian los nombres de métodos de los servicios, normalmente solo hay que ajustar este archivo y las rutas."""
from datetime import date
from functools import wraps
from flask import session, redirect, url_for, request
from services import usuario_service, catalogo_service, devolucion_service
from models import Estado


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not session.get("bibliotecario"):
            return redirect(url_for("auth.login", siguiente=request.path))
        return vista(*args, **kwargs)
    return envoltura


def fila_prestamo(p):
    """Une un préstamo con su usuario, ejemplar, libro, devolución y retraso para mostrarlo."""
    usuario = usuario_service.obtener(p.id_usuario)
    ejemplar = catalogo_service.obtener_ejemplar(p.id_ejemplar)
    libro = catalogo_service.obtener_libro(ejemplar.id_titulo)
    devolucion = devolucion_service.de_prestamo(p.id_prestamo)
    retraso = devolucion_service.retraso_de(p.id_prestamo)
    vencido = p.estado == Estado.ACTIVO and p.fecha_devolucion_estimada < date.today()
    dias = (date.today() - p.fecha_devolucion_estimada).days if vencido else (retraso.dias_retraso if retraso else 0)
    return {"p": p, "usuario": usuario, "ejemplar": ejemplar, "libro": libro,
            "devolucion": devolucion, "vencido": vencido, "dias_retraso": dias}
