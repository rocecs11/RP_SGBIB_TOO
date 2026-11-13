"""Punto de entrada: crea la aplicación Flask y registra los módulos (paquete `app`)."""
from flask import Flask
import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    from routes.auth_routes import auth_bp
    from routes.usuarios_routes import usuarios_bp
    from routes.catalogo_routes import catalogo_bp
    from routes.prestamos_routes import prestamos_bp
    from routes.consultas_routes import consultas_bp
    for bp in (auth_bp, usuarios_bp, catalogo_bp, prestamos_bp, consultas_bp):
        app.register_blueprint(bp)

    @app.template_filter("fecha")
    def fecha(valor):
        return valor.strftime("%d/%m/%Y") if valor else "—"

    @app.context_processor
    def globales():
        return {"nombre_biblioteca": config.NOMBRE_BIBLIOTECA}

    return app


if __name__ == "__main__":
    create_app().run(debug=False)   # debug=True solo durante el desarrollo
