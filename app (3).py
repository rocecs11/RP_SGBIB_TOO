{% extends "base.html" %}{% from "_macros.html" import badge %}
{% block titulo %}¿Quién lo tiene?{% endblock %}
{% block contenido %}
<header class="encabezado"><div><h1>¿Quién tiene este ejemplar?</h1><p class="muted">Escriba el código del ejemplar para ver quién lo tiene y cuándo debe devolverlo.</p></div></header>
<section class="panel">
  <form class="buscador" method="get"><input name="codigo" value="{{ codigo }}" placeholder="Código del ejemplar, ej. CC-001" autofocus><button class="btn primario">Buscar</button></form>
  {% if buscado %}
    {% if not ejemplar %}<p class="vacio">No existe un ejemplar con el código «{{ codigo }}».</p>
    {% else %}
    <div class="resultado-grande">
      <h3>{{ libro.titulo }} <small class="muted">· {{ ejemplar.codigo }}</small></h3>
      <p>Estado: {{ badge(ejemplar.estado) }}{% if ejemplar.motivo %} <small class="muted">({{ ejemplar.motivo }})</small>{% endif %}</p>
      {% if prestamo %}
        <div class="resumen"><div><span class="muted pequeño">Lo tiene</span><b>{{ usuario.nombre_completo }}</b><small>{{ usuario.identificacion }} · {{ usuario.telefono }}</small></div>
          <div><span class="muted pequeño">Desde</span><b>{{ prestamo.fecha_prestamo|fecha }}</b></div>
          <div><span class="muted pequeño">Debe devolverlo</span><b>{{ prestamo.fecha_devolucion_estimada|fecha }}</b></div></div>
      {% else %}<p class="muted">Este ejemplar no tiene un préstamo activo.</p>{% endif %}
    </div>
    {% endif %}
  {% endif %}
</section>
{% endblock %}
