from flask import Blueprint, request, g
from .quiz_functions import create_quiz

quiz_blueprint = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_blueprint.route('/', methods=("POST", "GET"))
def quiz_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_quiz(request)
