from flask import Blueprint, g, jsonify
from . models import Submission, Homework
from internal.decorators import permissions_required
from internal.exceptions import UnauthorizedError
from internal.helper import get_record_by_id

homework_blueprint = Blueprint('homework', __name__, url_prefix='/homework')


@homework_blueprint.route('/submissions')
@permissions_required({'Student'})
def list_my_submissions():
    submissions = Submission.query.filter_by(user_id=g.user.id)
    submissions_list = [s.to_dict(nest_homework=True, nest_comments=True) for s in submissions]
    return jsonify({'success': True, 'submissions': submissions_list})


@homework_blueprint.route('/homework/<int:homework_id>/submissions')
@permissions_required({'Teacher'})
def list_submissions(homework_id):
    homework = get_record_by_id(homework_id, Homework, check_school_id=False)
    if homework.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()
    submissions = Submission.query.filter_by(homework_id=homework.id).all()
    return jsonify({'success': True, 'submissions': [s.to_dict(nest_user=True) for s in submissions]})


@homework_blueprint.route('/due/<int:lesson_id>')
def homework_due_for_lesson(lesson_id):
    homework = Homework.query.filter(Homework.lesson_id == lesson_id)
    return jsonify({'success': True, 'homework': [h.to_dict(date_as_string=True) for h in homework]})
