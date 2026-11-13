"""Conexión a SQLite y manejo de transacciones (paquete `repositories`).

- `sesion()`: la usan los repositorios en cada operación. Si hay una transacción abierta con
  `transaccion()`, reutiliza su conexión; si no, abre una conexión corta (autocommit).
- `transaccion()`: agrupa varias operaciones en una sola unidad atómica (todo o nada).
  Usa BEGIN IMMEDIATE, de modo que dos solicitudes simultáneas se ejecutan una detrás de otra
  (RF-16: como máximo un préstamo activo por ejemplar).
- `inicializar()`: crea el archivo y las tablas desde database/schema.sql si aún no existen.
"""
import os
import sqlite3
import threading
from contextlib import contextmanager

import config

_local = threading.local()


def ruta_bd():
    """Ruta del archivo .db (SGBIB_DB tiene prioridad sobre config.DB_PATH)."""
    return os.environ.get("SGBIB_DB") or config.DB_PATH


def _conectar():
    ruta = ruta_bd()
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    con = sqlite3.connect(ruta, timeout=10, isolation_level=None)   # autocommit; BEGIN manual
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    # lower() de SQLite solo reconoce ASCII; esta función permite buscar sin distinguir mayúsculas con tildes
    con.create_function("minus", 1, lambda s: (s or "").lower(), deterministic=True)
    return con


@contextmanager
def sesion():
    """Conexión para un repositorio: la de la transacción en curso o una nueva y corta."""
    actual = getattr(_local, "con", None)
    if actual is not None:
        yield actual
        return
    con = _conectar()
    try:
        yield con
    finally:
        con.close()


@contextmanager
def transaccion():
    """Bloque atómico: confirma al salir bien y revierte todo si ocurre cualquier excepción."""
    if getattr(_local, "con", None) is not None:       # transacciones anidadas: se une a la exterior
        yield
        return
    con = _conectar()
    _local.con = con
    try:
        con.execute("BEGIN IMMEDIATE")
        yield
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
    finally:
        _local.con = None
        con.close()


def inicializar(forzar=False):
    """Crea las tablas si faltan. Con forzar=True borra el archivo y lo crea de cero."""
    ruta = ruta_bd()
    if forzar and os.path.exists(ruta):
        os.remove(ruta)
    with open(config.SCHEMA_PATH, encoding="utf-8") as f:
        esquema = f.read()
    con = _conectar()
    try:
        con.executescript(esquema)
    finally:
        con.close()
