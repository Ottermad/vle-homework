from flask import Blueprint, g, jsonify, request
from . models import Submission, Homework
from internal.decorators import permissions_required
from internal.exceptions import UnauthorizedError, CustomError
from internal.helper import get_record_by_id, get_boolean_query_param
from app import services

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


@homework_blueprint.route('/summary')
@permissions_required({"Student"})
def homework_due_summary():
    params = {'student_ids': g.user.id}
    resp = services.lesson.get('lessons/lesson', params=params)
    if resp.status_code != 200:
        raise CustomError(
            **resp.json()
        )

    lesson_ids = [l['id'] for l in resp.json()['lessons']]
    homework = Homework.query.filter(Homework.lesson_id.in_(lesson_ids))
    nest_lessons = get_boolean_query_param(request, 'nest-lessons')
    homework_list = [h.to_dict(date_as_string=True, nest_lesson=nest_lessons, has_submitted=True, user_id=g.user.id) for h in homework]

    return jsonify({'success': True, 'homework': homework_list})
