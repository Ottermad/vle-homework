from flask import Blueprint
from . models import *

quiz_blueprint = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_blueprint.route("/")
def index():
    return "Quiz Index"
