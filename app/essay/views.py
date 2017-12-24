from flask import Blueprint, g, request, jsonify
from internal.helper import get_record_by_id
from internal.exceptions import UnauthorizedError, CustomError
from . models import EssaySubmission
from .essay_functions import create_essay, submit_essay, essay_detail
from app import services

essay_blueprint = Blueprint('essay', __name__, url_prefix='/essay')


# Essay Routes
@essay_blueprint.route('/', methods=("POST",))
def essay_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_essay(request)


@essay_blueprint.route('/<int:essay_id>', methods=("POST", "GET"))
def essay_submit(essay_id):
    if request.method == "POST":
        return submit_essay(request, essay_id)
    else:
        return essay_detail(request, essay_id)


@essay_blueprint.route('/submission/<int:submission_id>')
def view_essay_submission(submission_id):
    if not (g.user.has_permissions({'Teacher'}) or g.user.has_permissions({'Student'})):
        raise UnauthorizedError()

    submission = get_record_by_id(submission_id, EssaySubmission, check_school_id=False)

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
