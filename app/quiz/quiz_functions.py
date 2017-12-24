import datetime

from flask import g, jsonify

from internal.helper import json_from_request, check_keys,get_record_by_id
from internal.exceptions import UnauthorizedError,  CustomError

from app import services, db
from .models import Quiz, Question, QuizAnswer, QuizSubmission


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


def submit_quiz(request, quiz_id):
    # Check quiz is valid
    quiz = get_record_by_id(quiz_id, Quiz, check_school_id=False)
    #  Validate lesson
    resp = services.lesson.get(
        "lessons/lesson/{}".format(quiz.lesson_id), 
        headers=g.user.headers_dict(),
        params={'nest-students': True}
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if lesson['school_id'] != g.user.school_id:
        raise UnauthorizedError()

    json_data = json_from_request(request)
    expected_top_keys = ['answers']
    expected_inner_keys = ['question_id', 'answer']

    check_keys(expected_top_keys, json_data)

    if g.user.id not in [t['id'] for t in lesson['students']]:
        raise UnauthorizedError()

    question_ids = [question.id for question in quiz.questions]

    submission = QuizSubmission(
        homework_id=quiz.id,
        user_id=g.user.id,
        datetime_submitted=datetime.datetime.now()  # TODO: Deal with timezones
    )

    for answer in json_data['answers']:
        check_keys(expected_inner_keys, answer)
        question = get_record_by_id(answer['question_id'], Question, check_school_id=False)
        if question.id not in question_ids:
            raise UnauthorizedError()

        answer = QuizAnswer(answer['answer'], submission.id, question.id)
        submission.answers.append(answer)

    submission.mark()
    db.session.add(submission)
    db.session.commit()
    return jsonify({'score': submission.total_score})


def quiz_detail(request, quiz_id):
    # Check quiz if valid
    quiz = get_record_by_id(quiz_id, Quiz, check_school_id=False)

    resp = services.lesson.get(
        "lessons/lesson/{}".format(quiz.lesson_id), 
        headers=g.user.headers_dict(),
    )
    if resp.status_code != 200:
        raise CustomError(**resp.json())

    lesson = resp.json()['lesson']

    if lesson['school_id'] != g.user.school_id:
        raise UnauthorizedError()

    return jsonify({'success': True, 'quiz': quiz.to_dict()})
