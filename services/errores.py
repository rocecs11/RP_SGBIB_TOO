class ReglaNegocioError(Exception):
    """Se lanza cuando una operación incumple una regla de negocio o una validación.
    El mensaje se muestra tal cual al bibliotecario."""
