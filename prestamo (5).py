class Libro:
    def __init__(self, id_titulo, isbn, titulo, autor, editorial="", anio_publicacion=None, categoria=""):
        self.id_titulo = id_titulo
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.anio_publicacion = anio_publicacion
        self.categoria = categoria
