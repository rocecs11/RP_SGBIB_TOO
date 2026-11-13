from flask import Blueprint, render_template, request, redirect, url_for, flash
from services import usuario_service, ReglaNegocioError
from ._helpers import login_requerido

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
@login_requerido
def lista():
    q = request.args.get("q", "")
    return render_template("usuarios.html", usuarios=usuario_service.listar(q), q=q)


@usuarios_bp.route("/nuevo", methods=["POST"])
@login_requerido
def nuevo():
    try:
        u = usuario_service.registrar(request.form.get("nombre"), request.form.get("apellido"), request.form.get("tipo"),
                                      request.form.get("identificacion"), request.form.get("correo"), request.form.get("telefono"))
        flash(f"Usuario {u.nombre_completo} registrado como habilitado.", "success")
    except ReglaNegocioError as e:
        flash(str(e), "error")
    return redirect(url_for("usuarios.lista"))


@usuarios_bp.route("/<int:id_usuario>/estado", methods=["POST"])
@login_requerido
def estado(id_usuario):
    try:
        u = usuario_service.cambiar_estado(id_usuario, request.form.get("habilitado") == "1")
        flash(f"{u.nombre_completo} ahora está {'habilitado' if u.habilitado else 'inhabilitado'}.", "success")
    except ReglaNegocioError as e:
        flash(str(e), "error")
    return redirect(url_for("usuarios.lista"))
