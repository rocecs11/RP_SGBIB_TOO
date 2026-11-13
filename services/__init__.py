"""Servicios de negocio. La interfaz (routes/) solo usa estas instancias.
Las reglas de negocio se aplican aquí; el acceso a datos se delega en el paquete `repositories` (SQLite)."""
from .errores import ReglaNegocioError
from .autenticacion_service import AutenticacionService
from .usuario_service import UsuarioService
from .catalogo_service import CatalogoService
from .prestamo_service import PrestamoService
from .devolucion_service import DevolucionService
from .consulta_service import ConsultaService

autenticacion_service = AutenticacionService()
usuario_service = UsuarioService()
catalogo_service = CatalogoService()
prestamo_service = PrestamoService()
devolucion_service = DevolucionService()
consulta_service = ConsultaService()
