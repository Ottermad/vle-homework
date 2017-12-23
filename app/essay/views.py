from flask import Blueprint
from . models import *

essay_blueprint = Blueprint('essay', __name__, url_prefix='/essay')


@essay_blueprint.route("/")
def index():
    return "Essay Index"
