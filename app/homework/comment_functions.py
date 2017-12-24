"""Functions to manipulate Comments."""
from flask import g, jsonify
from app import db, services
from internal.exceptions import UnauthorizedError, CustomError
from internal.helper import json_from_request, check_keys, get_record_by_id
from app.homework.models import Submission, Comment


def comment_create_view(request):
    """Creates a Comment object from a HTTP request."""

    # Keys which need to in JSON from request
    top_level_expected_keys = [
        "submission_id",
        "text",
    ]

    # Get JSON from request and check keys are present
    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)

    #  Fetch submission
    submission = get_record_by_id(json_data['submission_id'], Submission, check_school_id=False)

    # Check user teaches the lesson that submission they are commenting on
    resp = services.lesson.get(
        "lessons/lesson/{}".format(submission.homework.lesson_id), 
        headers=g.user.headers_dict(),
        params={'nest-teachers': True}
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if g.user.id not in [t['id'] for t in lesson['teachers']]:
        raise UnauthorizedError()

    # Create comment
    comment = Comment(submission.id, json_data['text'], g.user.id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"success": True, "comment": comment.to_dict()}), 201


def comment_detail_view(request, comment_id):
    """Fetch Comment based on id from request."""
    comment = get_record_by_id(comment_id, Comment, check_school_id=False)

    # Check user teaches the lesson that submission they are commenting on
    resp = services.lesson.get(
        "lessons/lesson/{}".format(comment.submission.homework.lesson_id), 
        headers=g.user.headers_dict(),
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if g.user.id != lesson['school_id']:
        raise UnauthorizedError()

    return jsonify({'success': True, 'comment': comment.to_dict(nest_user=True)})


def comment_delete_view(request, comment_id):
    """Delete Comment based on id."""
    comment = get_record_by_id(comment_id, Comment, check_school_id=False)
    
    # Check user teaches the lesson that submission they are commenting on
    resp = services.lesson.get(
        "lessons/lesson/{}".format(comment.submission.homework.lesson_id), 
        headers=g.user.headers_dict(),
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if g.user.id != lesson['school_id']:
        raise UnauthorizedError()
    
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted.'})


def comment_update_view(request, comment_id):
    """Update Comment based on id."""
    # Get comment
    comment = get_record_by_id(comment_id, Comment)

    # Validate that user has permission
    if comment.user_id != g.user.id:
        raise UnauthorizedError()

    # Get JSON data
    data = json_from_request(request)

    # If text in data, then update the text
    if 'text' in data.keys():
        comment.name = data['text']

    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Updated.'})
