"""Conversiones comunes entre filas SQLite y objetos del dominio."""
from datetime import date


def a_fecha(texto):
    return date.fromisoformat(texto) if texto else None


def de_fecha(valor):
    return valor.isoformat() if valor else None


def patron(texto):
    """Texto de búsqueda en minúsculas y sin espacios sobrantes ('' = sin filtro)."""
    return (texto or "").strip().lower()
