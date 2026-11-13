from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from services import (usuario_service, catalogo_service, prestamo_service, devolucion_service, ReglaNegocioError)
from ._helpers import login_requerido, fila_prestamo

prestamos_bp = Blueprint("prestamos", __name__)


@prestamos_bp.route("/prestamos")
@login_requerido
def activos():
    q = request.args.get("q", "")
    filas = [fila_prestamo(p) for p in prestamo_service.listar_activos(q)]
    return render_template("prestamos_activos.html", filas=filas, q=q, modo="prestamos")


@prestamos_bp.route("/prestamos/nuevo", methods=["GET", "POST"])
@login_requerido
def nuevo():
    if request.method == "POST":
        try:
            p = prestamo_service.registrar(request.form.get("id_usuario"), request.form.get("id_ejemplar"))
            f = fila_prestamo(p)
            flash(f"Préstamo registrado: «{f['libro'].titulo}» ({f['ejemplar'].codigo}) para {f['usuario'].nombre_completo}. "
                  f"Debe devolverlo el {p.fecha_devolucion_estimada.strftime('%d/%m/%Y')}.", "success")
            return redirect(url_for("prestamos.activos"))
        except ReglaNegocioError as e:
            flash(str(e), "error")
    ejemplares = [(e, catalogo_service.obtener_libro(e.id_titulo)) for e in catalogo_service.listar_ejemplares()]
    return render_template("prestamo_nuevo.html", usuarios=usuario_service.listar(), ejemplares=ejemplares,
                           sel_usuario=request.form.get("id_usuario", ""), sel_ejemplar=request.form.get("id_ejemplar", ""))


@prestamos_bp.route("/devoluciones")
@login_requerido
def devoluciones():
    q = request.args.get("q", "")
    filas = [fila_prestamo(p) for p in prestamo_service.listar_activos(q)]
    return render_template("prestamos_activos.html", filas=filas, q=q, modo="devoluciones")


@prestamos_bp.route("/prestamos/<int:id_prestamo>/devolver", methods=["GET", "POST"])
@login_requerido
def devolver(id_prestamo):
    p = prestamo_service.obtener(id_prestamo)
    if not p:
        abort(404)
    if request.method == "POST":
        try:
            d, retraso = devolucion_service.registrar(id_prestamo, request.form.get("observaciones"),
                                                      request.form.get("fuera_de_servicio") == "1", request.form.get("motivo"))
            if retraso:
                flash(f"Devolución registrada con {retraso.dias_retraso} día(s) de retraso, asociado al préstamo y al usuario.", "warning")
            else:
                flash("Devolución registrada a tiempo. El ejemplar quedó actualizado.", "success")
            return redirect(url_for("prestamos.devoluciones"))
        except ReglaNegocioError as e:
            flash(str(e), "error")
    return render_template("devolucion.html", f=fila_prestamo(p))
