from flask import Flask

from qr_tabulator.views import base_blueprint


def create_app(testing=False, cli=False):
    """Application factory, used to create application"""
    app = Flask("qr_tabulator")
    app.config.from_object("qr_tabulator.config")
    app.config["TESTING"] = testing

    register_blueprints(app)

    return app


def register_blueprints(app):
    """register all blueprints for application"""
    app.register_blueprint(base_blueprint)
