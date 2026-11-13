from datetime import date, timedelta
from flask import Blueprint, render_template, request
from services import consulta_service, usuario_service, catalogo_service
from ._helpers import login_requerido, fila_prestamo

consultas_bp = Blueprint("consultas", __name__)


@consultas_bp.route("/")
@login_requerido
def inicio():
    r = consulta_service.resumen()
    filas = [fila_prestamo(p) for p in consulta_service.historial("usuario", "")]
    vencidos = [f for f in filas if f["vencido"]]
    hoy = date.today()
    nombres = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    dias = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        dias.append({"etiqueta": f"{nombres[d.weekday()]} {d.day}", "total": sum(f["p"].fecha_prestamo == d for f in filas)})
    mayor = max([d["total"] for d in dias] + [1])
    for d in dias:
        d["pct"] = round(d["total"] / mayor * 100)
    total = max(r["disponibles"] + r["prestados"] + r["fuera_servicio"], 1)
    pa = round(r["disponibles"] / total * 100, 1)
    pb = round(pa + r["prestados"] / total * 100, 1)
    eventos = []
    for f in filas:
        u, l = f["usuario"].nombre_completo, f["libro"].titulo
        eventos.append({"fecha": f["p"].fecha_prestamo, "color": "azul", "texto": f"{u} tomó «{l}» ({f['ejemplar'].codigo})"})
        if f["devolucion"]:
            tarde = f["dias_retraso"] > 0
            eventos.append({"fecha": f["devolucion"].fecha_devolucion, "color": "rojo" if tarde else "verde",
                            "texto": f"{u} devolvió «{l}»" + (f" con {f['dias_retraso']} día(s) de retraso" if tarde else "")})
    actividad = sorted(eventos, key=lambda e: e["fecha"], reverse=True)[:7]
    return render_template("inicio.html", r=r, vencidos=vencidos, dias=dias, pa=pa, pb=pb, actividad=actividad)


@consultas_bp.route("/consultas/disponibilidad")
@login_requerido
def disponibilidad():
    q = request.args.get("q", "")
    return render_template("disponibilidad.html", resultados=consulta_service.disponibilidad(q), q=q)


@consultas_bp.route("/consultas/poseedor")
@login_requerido
def poseedor():
    codigo = request.args.get("codigo", "")
    ejemplar = prestamo = libro = usuario = None
    buscado = bool(codigo.strip())
    if buscado:
        ejemplar, prestamo = consulta_service.poseedor(codigo)
        if ejemplar:
            libro = catalogo_service.obtener_libro(ejemplar.id_titulo)
        if prestamo:
            usuario = usuario_service.obtener(prestamo.id_usuario)
    return render_template("poseedor.html", codigo=codigo, buscado=buscado, ejemplar=ejemplar, libro=libro,
                           prestamo=prestamo, usuario=usuario)


@consultas_bp.route("/consultas/historial")
@login_requerido
def historial():
    tipo, q = request.args.get("tipo", "usuario"), request.args.get("q", "")
    filas = [fila_prestamo(p) for p in consulta_service.historial(tipo, q)]
    return render_template("historial.html", filas=filas, tipo=tipo, q=q)
