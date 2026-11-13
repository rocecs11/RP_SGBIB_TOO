{% extends "base.html" %}{% from "_macros.html" import badge %}
{% block titulo %}Catálogo{% endblock %}
{% block contenido %}
<header class="encabezado"><div><h1>Catálogo</h1><p class="muted">Títulos y sus ejemplares físicos.</p></div></header>

<details class="panel plegable">
  <summary>+ Registrar nuevo título</summary>
  <form method="post" action="{{ url_for('catalogo.nuevo_libro') }}" class="formulario rejilla">
    <label>Título *<input name="titulo" required></label>
    <label>Autor *<input name="autor" required></label>
    <label>ISBN *<input name="isbn" required placeholder="978-…"></label>
    <label>Editorial<input name="editorial"></label>
    <label>Año de publicación<input name="anio_publicacion" inputmode="numeric"></label>
    <label>Categoría<input name="categoria"></label>
    <div class="acciones"><button class="btn primario">Guardar título</button><span class="muted pequeño">Luego podrá agregar sus ejemplares.</span></div>
  </form>
</details>

<section class="panel">
  <form class="buscador" method="get"><input name="q" value="{{ q }}" placeholder="Buscar por título, autor o ISBN…"><button class="btn">Buscar</button></form>
  {% if libros %}
  <table><thead><tr><th>Título</th><th>Autor</th><th>ISBN</th><th>Categoría</th><th>Ejemplares</th><th></th></tr></thead><tbody>
  {% for l, ejs in libros %}<tr>
    <td><b>{{ l.titulo }}</b><br><small class="muted">{{ l.editorial }} {{ l.anio_publicacion or '' }}</small></td>
    <td>{{ l.autor }}</td><td>{{ l.isbn }}</td><td>{{ l.categoria or '—' }}</td>
    <td>{{ ejs|selectattr('estado','equalto','disponible')|list|length }} disponibles de {{ ejs|length }}</td>
    <td class="der"><a class="btn pequeño" href="{{ url_for('catalogo.detalle', id_titulo=l.id_titulo) }}">Ver ejemplares</a></td></tr>{% endfor %}
  </tbody></table>
  {% else %}<p class="vacio">No se encontraron títulos.</p>{% endif %}
</section>
{% endblock %}
