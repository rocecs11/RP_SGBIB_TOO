from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import autenticacion_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        b = autenticacion_service.iniciar_sesion(request.form.get("usuario"), request.form.get("contrasena"))
        if b:
            session["bibliotecario"] = b.nombre
            destino = request.args.get("siguiente") or url_for("consultas.inicio")
            return redirect(destino if destino.startswith("/") else url_for("consultas.inicio"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
