import requests
from flask import Blueprint, abort, current_app, jsonify, request, send_file
from flask.json import JSONEncoder
from qr_tabulator.models.tabulator import tabulate_qr, write_table

base_blueprint = Blueprint("base", __name__, cli_group=None)


@base_blueprint.route("/")
def root():
    return {"message": "ok"}


@base_blueprint.route("/settings", defaults={"config_key": None})
@base_blueprint.route("/settings/<string:config_key>")
def config_settings(config_key):
    """Non-secret application settings"""

    # workaround no JSON representation for datetime.timedelta
    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            return str(obj)

    current_app.json_encoder = CustomJSONEncoder

    # return selective keys - not all can be be viewed by users, e.g.secret key
    blacklist = ("SECRET", "KEY")

    if config_key:
        key = config_key.upper()
        for pattern in blacklist:
            if pattern in key:
                abort(status_code=400, messag=f"Configuration key {key} not available")
        return jsonify({key: current_app.config.get(key)})

    settings = {}
    for key in current_app.config:
        matches = any(pattern for pattern in blacklist if pattern in key)
        if matches:
            continue
        settings[key] = current_app.config.get(key)

    return jsonify(settings)


@base_blueprint.route("/tabulate", methods=['POST'])
def tabulate():
    """convert bundle of FHIR QuestionnaireResponse to CSV"""
    # response.raise_for_status()
    data = request.get_json()
    table = tabulate_qr(data)
    path = write_table(table)
    return send_file(path, as_attachment=True)
