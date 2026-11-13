<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titulo %}Panel{% endblock %} · SGBIB</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}">
</head>
<body>
{% set ep = request.endpoint or '' %}
<div class="app">
  <aside class="lateral">
    <div class="marca"><span class="logo">📚</span><div><strong>SGBIB</strong><small>{{ nombre_biblioteca }}</small></div></div>
    <nav>
      <a href="{{ url_for('consultas.inicio') }}" class="{{ 'activo' if ep == 'consultas.inicio' }}">Inicio</a>
      <a href="{{ url_for('usuarios.lista') }}" class="{{ 'activo' if ep.startswith('usuarios.') }}">Usuarios</a>
      <a href="{{ url_for('catalogo.lista') }}" class="{{ 'activo' if ep.startswith('catalogo.') }}">Catálogo</a>
      <a href="{{ url_for('prestamos.activos') }}" class="{{ 'activo' if ep in ('prestamos.activos','prestamos.nuevo') }}">Préstamos</a>
      <a href="{{ url_for('prestamos.devoluciones') }}" class="{{ 'activo' if ep in ('prestamos.devoluciones','prestamos.devolver') }}">Devoluciones</a>
      <span class="grupo">Consultas</span>
      <a class="sub {{ 'activo' if ep == 'consultas.disponibilidad' }}" href="{{ url_for('consultas.disponibilidad') }}">Disponibilidad</a>
      <a class="sub {{ 'activo' if ep == 'consultas.poseedor' }}" href="{{ url_for('consultas.poseedor') }}">¿Quién lo tiene?</a>
      <a class="sub {{ 'activo' if ep == 'consultas.historial' }}" href="{{ url_for('consultas.historial') }}">Historial</a>
    </nav>
    <div class="sesion">
      <span class="avatar">{{ session.get('bibliotecario', '?')[0] }}</span>
      <div><strong>{{ session.get('bibliotecario') }}</strong><small>Bibliotecario</small></div>
      <a href="{{ url_for('auth.logout') }}" title="Cerrar sesión" class="salir">Salir</a>
    </div>
  </aside>
  <main class="contenido">
    {% with mensajes = get_flashed_messages(with_categories=true) %}
      {% for categoria, texto in mensajes %}<div class="aviso {{ categoria }}">{{ texto }}<button type="button" class="cerrar" aria-label="Cerrar">×</button></div>{% endfor %}
    {% endwith %}
    {% block contenido %}{% endblock %}
  </main>
</div>
<script>
  // Avisos: se pueden cerrar y los de éxito se ocultan solos
  document.querySelectorAll('.aviso').forEach(a => {
    const ocultar = () => { a.classList.add('saliendo'); setTimeout(() => a.remove(), 350); };
    a.querySelector('.cerrar')?.addEventListener('click', ocultar);
    if (a.classList.contains('success')) setTimeout(ocultar, 6000);
  });
  // Contadores animados
  document.querySelectorAll('[data-valor]').forEach(el => {
    const fin = parseInt(el.dataset.valor, 10) || 0, t0 = performance.now(), dur = 900;
    const paso = t => { const p = Math.min((t - t0) / dur, 1); el.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(paso); };
    requestAnimationFrame(paso);
  });
  // Búsqueda en vivo: filtra la tabla (o los bloques) mientras se escribe
  document.querySelectorAll('.buscador input[name="q"]').forEach(inp => {
    const filas = () => document.querySelectorAll('.panel table tbody tr, .libro-bloque');
    inp.addEventListener('input', () => {
      const t = inp.value.trim().toLowerCase();
      filas().forEach(f => f.style.display = (!t || f.textContent.toLowerCase().includes(t)) ? '' : 'none');
    });
  });
  // Reloj y fecha en vivo
  const reloj = document.getElementById('reloj'), fecha = document.getElementById('fecha-hoy');
  if (reloj) {
    const tick = () => { const d = new Date();
      reloj.textContent = d.toLocaleTimeString('es-SV', {hour: '2-digit', minute: '2-digit', second: '2-digit'});
      if (fecha) fecha.textContent = d.toLocaleDateString('es-SV', {weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'}); };
    tick(); setInterval(tick, 1000);
  }
</script>
{% block scripts %}{% endblock %}
</body>
</html>
