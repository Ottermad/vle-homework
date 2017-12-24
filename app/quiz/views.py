from flask import Blueprint, request, g, jsonify
from .quiz_functions import create_quiz, submit_quiz, quiz_detail
from internal.decorators import permissions_required
from internal.exceptions import UnauthorizedError, CustomError
from app import services
from internal.helper import get_record_by_id
from .models import QuizSubmission

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


@quiz_blueprint.route('/submission/<int:submission_id>')
def view_quiz_submission(submission_id):
    if not (g.user.has_permissions({'Teacher'}) or g.user.has_permissions({'Student'})):
        raise UnauthorizedError()

    submission = get_record_by_id(submission_id, QuizSubmission, check_school_id=False)
    # Validate lesson
    resp = services.lesson.get(
        "lessons/lesson/{}".format(submission.homework.lesson_id), 
        headers=g.user.headers_dict(),
        params={'nest-students': True}
    )

    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if lesson['school_id'] != g.user.school_id:
        raise UnauthorizedError()
    return jsonify({'success': True, 'submission': submission.to_dict(nest_user=True, nest_homework=True, nest_comments=True)})
