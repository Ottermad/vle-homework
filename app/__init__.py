"""Main Package."""
from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from config import config
from services import Services
from internal.exceptions import CustomError
from internal.auth_helper import ProxiedUser

db = SQLAlchemy()
services = Services()


def create_app(config_name="default"):
    """Create Flask object called app and return it."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    @app.errorhandler(CustomError)
    def custom_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found_handler(error):
        response = jsonify({'status_code': 404, 'error': True, 'message': 'Not Found'})
        response.status_code = 404
        return response

    @app.before_request
    def get_user_details_from_header():
        g.user = ProxiedUser(request.headers)

    db.init_app(app)
    services.init_app(app)

    from .homework.views import homework_blueprint
    app.register_blueprint(homework_blueprint)

    return app
