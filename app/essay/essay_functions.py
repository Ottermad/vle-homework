"""Essay Functions."""
import datetime

from flask import g, jsonify

from app import db, services
from internal.exceptions import UnauthorizedError, CustomError
from internal.helper import json_from_request, check_keys, get_record_by_id
# from app.homework.models import Essay, HomeworkType, Question, QuizAnswer, QuizSubmission, EssaySubmission
# from app.lessons.models import Lesson
from .models import Essay, EssaySubmission


def create_essay(request):
    """Function to create an essay from request."""
    # List of keys needed to create an Essay
    top_level_expected_keys = [
        "lesson_id",
        "title",
        "description",
        "date_due",
    ]

    # Extract JSON from request and check keys are present
    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)

    # Validate lesson
    resp = services.lesson.get(
        "lessons/lesson/{}".format(json_data['lesson_id']), 
        headers=g.user.headers_dict(),
        params={'nest-teachers': True}
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if g.user.id not in [t['id'] for t in lesson['teachers']]:
        raise UnauthorizedError()

    # Validate date
    date_due_string = json_data['date_due']
    try:
        date_due = datetime.datetime.strptime(date_due_string, "%d/%m/%Y").date()
    except ValueError:
        raise CustomError(409, message="Invalid date_due: {}.".format(json_data['date_due']))

    # Create Essay
    essay = Essay(
        lesson_id=json_data['lesson_id'],
        title=json_data['title'],
        description=json_data['description'],
        date_due=date_due,
    )

    db.session.add(essay)
    db.session.commit()

    return jsonify(essay.to_dict()), 201


def submit_essay(request, essay_id):
    # Check essay if valid
    essay = get_record_by_id(essay_id, Essay, check_school_id=False)
    
    # Validate lesson
    resp = services.lesson.get(
        "lessons/lesson/{}".format(essay.lesson_id), 
        headers=g.user.headers_dict(),
        params={'nest-students': True}
    )

    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if lesson['school_id'] != g.user.school_id:
        raise UnauthorizedError()

    top_level_expected_keys = [
        "content"
    ]
    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)


    if g.user.id not in [t['id'] for t in lesson['students']]:
        raise UnauthorizedError()

    submission = EssaySubmission(
        essay.id,
        g.user.id,
        datetime.datetime.now(),  #  TODO: Deal with timezones
        json_data['content']
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({'success': True}), 201


def essay_detail(request, essay_id):
    # Check essay if valid
    essay = get_record_by_id(essay_id, Essay, check_school_id=False)

    resp = services.lesson.get(
        "lessons/lesson/{}".format(essay.lesson_id), 
        headers=g.user.headers_dict(),
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if lesson['school_id'] != g.user.school_id:
        raise UnauthorizedError()

    return jsonify({'success': True, 'essay': essay.to_dict()})
