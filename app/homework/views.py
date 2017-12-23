from flask import Blueprint
from . models import *

homework_blueprint = Blueprint('homework', __name__)


@homework_blueprint.route("/")
def index():
    return "Homework Index"
