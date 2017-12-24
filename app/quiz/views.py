from flask import Blueprint, request, g
from .quiz_functions import create_quiz, submit_quiz, quiz_detail
from internal.decorators import permissions_required

quiz_blueprint = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_blueprint.route('/', methods=("POST", "GET"))
def quiz_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_quiz(request)


@quiz_blueprint.route('/<int:quiz_id>', methods=("POST", "GET"))
@permissions_required({'Student'})
def quiz_submit(quiz_id):
    if request.method == "POST":
        return submit_quiz(request, quiz_id)
    return quiz_detail(request, quiz_id)