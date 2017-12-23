from flask import Blueprint
from . models import *

essay_blueprint = Blueprint('essay', __name__)


@essay_blueprint.route("/")
def index():
    return "Essay Index"
