{% extends "base.html" %}{% from "_macros.html" import badge %}
{% block titulo %}Usuarios{% endblock %}
{% block contenido %}
<header class="encabezado"><div><h1>Usuarios</h1><p class="muted">Personas registradas que pueden solicitar préstamos.</p></div></header>

<details class="panel plegable" {% if not usuarios %}open{% endif %}>
  <summary>+ Registrar nuevo usuario</summary>
  <form method="post" action="{{ url_for('usuarios.nuevo') }}" class="formulario rejilla">
    <label>Nombre *<input name="nombre" required></label>
    <label>Apellido *<input name="apellido" required></label>
    <label>Identificación *<input name="identificacion" required placeholder="Ej. U-2301"></label>
    <label>Tipo<select name="tipo"><option>Estudiante</option><option>Docente</option><option>Externo</option></select></label>
    <label>Correo<input type="email" name="correo"></label>
    <label>Teléfono<input name="telefono"></label>
    <div class="acciones"><button class="btn primario">Guardar usuario</button><span class="muted pequeño">Se registra como habilitado.</span></div>
  </form>
</details>

<section class="panel">
  <form class="buscador" method="get"><input name="q" value="{{ q }}" placeholder="Buscar por nombre, identificación o correo…"><button class="btn">Buscar</button></form>
  {% if usuarios %}
  <table><thead><tr><th>Identificación</th><th>Nombre</th><th>Tipo</th><th>Contacto</th><th>Estado</th><th></th></tr></thead><tbody>
  {% for u in usuarios %}<tr>
    <td>{{ u.identificacion }}</td><td><b>{{ u.nombre_completo }}</b></td><td>{{ u.tipo }}</td>
    <td>{{ u.correo or '—' }}<br><small class="muted">{{ u.telefono }}</small></td>
    <td>{{ badge('habilitado' if u.habilitado else 'inhabilitado') }}</td>
    <td class="der"><form method="post" action="{{ url_for('usuarios.estado', id_usuario=u.id_usuario) }}">
      <input type="hidden" name="habilitado" value="{{ '0' if u.habilitado else '1' }}">
      <button class="btn pequeño {{ 'peligro' if u.habilitado }}">{{ 'Inhabilitar' if u.habilitado else 'Habilitar' }}</button></form></td></tr>{% endfor %}
  </tbody></table>
  {% else %}<p class="vacio">No se encontraron usuarios.</p>{% endif %}
</section>
{% endblock %}
