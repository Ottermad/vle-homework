import datetime

from flask import g, jsonify

from internal.helper import json_from_request, check_keys,get_record_by_id
from internal.exceptions import UnauthorizedError,  CustomError

from app import services, db
from .models import Quiz, Question


def create_quiz(request):
    top_level_expected_keys = [
        "lesson_id",
        "title",
        "description",
        "date_due",
        "questions"
    ]
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

    quiz = Quiz(
        lesson_id=json_data['lesson_id'],
        title=json_data['title'],
        description=json_data['description'],
        date_due=date_due,
        number_of_questions=len(json_data['questions'])
    )

    db.session.add(quiz)
    db.session.commit()

    for question_object in json_data['questions']:
        if 'answer' and 'question_text' not in question_object.keys():
            raise CustomError(
                409,
                message="Invalid object in questions array. Make sure it has a question and a answer."
            )
        question = Question(quiz.id, question_object['question_text'], question_object['answer'])
        db.session.add(question)
        quiz.questions.append(question)

    db.session.add(quiz)
    db.session.commit()
    return jsonify(quiz.to_dict()), 201
