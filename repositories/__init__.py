"""Persistencia: guarda y recupera las entidades del paquete `models` en SQLite. Sin reglas de negocio."""
from . import db
from .bibliotecario_repository import BibliotecarioRepository
from .usuario_repository import UsuarioRepository
from .libro_repository import LibroRepository
from .ejemplar_repository import EjemplarRepository
from .prestamo_repository import PrestamoRepository
from .devolucion_repository import DevolucionRepository

bibliotecario_repo = BibliotecarioRepository()
usuario_repo = UsuarioRepository()
libro_repo = LibroRepository()
ejemplar_repo = EjemplarRepository()
prestamo_repo = PrestamoRepository()
devolucion_repo = DevolucionRepository()
