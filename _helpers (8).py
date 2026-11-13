from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from services import catalogo_service, ReglaNegocioError
from ._helpers import login_requerido

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/catalogo")


@catalogo_bp.route("/")
@login_requerido
def lista():
    q = request.args.get("q", "")
    libros = [(l, catalogo_service.listar_ejemplares(l.id_titulo)) for l in catalogo_service.listar_libros(q)]
    return render_template("catalogo.html", libros=libros, q=q)


@catalogo_bp.route("/libros/nuevo", methods=["POST"])
@login_requerido
def nuevo_libro():
    f = request.form
    try:
        l = catalogo_service.registrar_libro(f.get("titulo"), f.get("autor"), f.get("isbn"), f.get("editorial"),
                                             f.get("anio_publicacion"), f.get("categoria"))
        flash(f"Título «{l.titulo}» registrado. Ahora agregue sus ejemplares.", "success")
        return redirect(url_for("catalogo.detalle", id_titulo=l.id_titulo))
    except ReglaNegocioError as e:
        flash(str(e), "error")
        return redirect(url_for("catalogo.lista"))


@catalogo_bp.route("/libros/<int:id_titulo>")
@login_requerido
def detalle(id_titulo):
    libro = catalogo_service.obtener_libro(id_titulo)
    if not libro:
        abort(404)
    return render_template("ejemplares.html", libro=libro, ejemplares=catalogo_service.listar_ejemplares(id_titulo))


@catalogo_bp.route("/libros/<int:id_titulo>/ejemplares/nuevo", methods=["POST"])
@login_requerido
def nuevo_ejemplar(id_titulo):
    try:
        e = catalogo_service.registrar_ejemplar(id_titulo, request.form.get("codigo"), request.form.get("ubicacion"))
        flash(f"Ejemplar {e.codigo} registrado como disponible.", "success")
    except ReglaNegocioError as e:
        flash(str(e), "error")
    return redirect(url_for("catalogo.detalle", id_titulo=id_titulo))


@catalogo_bp.route("/ejemplares/<int:id_ejemplar>/estado", methods=["POST"])
@login_requerido
def estado_ejemplar(id_ejemplar):
    e = catalogo_service.obtener_ejemplar(id_ejemplar)
    if not e:
        abort(404)
    try:
        catalogo_service.cambiar_estado_ejemplar(id_ejemplar, request.form.get("estado"), request.form.get("motivo"))
        flash(f"Ejemplar {e.codigo}: estado actualizado a «{e.estado}».", "success")
    except ReglaNegocioError as err:
        flash(str(err), "error")
    return redirect(url_for("catalogo.detalle", id_titulo=e.id_titulo))
