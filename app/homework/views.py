from flask import Blueprint, g, jsonify
from . models import Submission
from internal.decorators import permissions_required

homework_blueprint = Blueprint('homework', __name__, url_prefix='/homework')


@homework_blueprint.route('/submissions')
@permissions_required({'Student'})
def list_my_submissions():
    submissions = Submission.query.filter_by(user_id=g.user.id)
    submissions_list = [s.to_dict(nest_homework=True, nest_comments=True) for s in submissions]
    return jsonify({'success': True, 'submissions': submissions_list})
