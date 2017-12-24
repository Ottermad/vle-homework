import datetime
from enum import Enum

from app import db, services

from internal.exceptions import CustomError

from flask import g


class HomeworkType(Enum):
    HOMEWORK = 0
    ESSAY = 1
    QUIZ = 2


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name


class Homework(db.Model):
    """Model representing a homework which can be assigned to a submission."""
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    date_due = db.Column(db.Date)

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.HOMEWORK.value,
        'polymorphic_on': type_id
    }

    def has_submitted(self, user_id):
        submission = Submission.query.filter_by(user_id=user_id, homework_id=self.id).first()
        return not (submission is None)

    def __init__(self, lesson_id, title, description, type_id, date_due):
        self.lesson_id = lesson_id
        self.title = title
        self.description = description
        self.type_id = type_id
        self.date_due = date_due

    def to_dict(self, date_as_string=False, nest_lesson=False, has_submitted=False, user_id=None):
        homework_dict = {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'type': HomeworkType(self.type_id).name,
            'date_due': self.date_due.strftime('%d/%m/%Y') if date_as_string else self.date_due
        }

        if nest_lesson:
            pass
            # TODO: Send request to lesson service
            # homework_dict['lesson'] = self.lesson.to_dict()

        if has_submitted:
            submission = Submission.query.filter_by(user_id=user_id, homework_id=self.id).first()
            has_submitted = not (submission is None)
            homework_dict['submitted'] = has_submitted
            if has_submitted:
                homework_dict['submission'] = submission.to_dict()

        return homework_dict


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    user_id = db.Column(db.Integer)
    datetime_submitted = db.Column(db.DateTime)

    homework = db.relationship('Homework', backref=db.backref('submissions'))
    comments = db.relationship('Comment', backref=db.backref('submission'))

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.HOMEWORK.value,
        'polymorphic_on': type_id
    }

    def __init__(self, homework_id, type_id, user_id, datetime_submitted):
        self.homework_id = homework_id
        self.type_id = type_id
        self.user_id = user_id
        self.datetime_submitted = datetime_submitted

    def to_dict(self, nest_user=False, nest_comments=False, nest_homework=False):
        submission_dict = {
            'id': self.id,
            'homework_id': self.homework_id,
            'user_id': self.user_id,
            'type_id': self.type_id,
            'type': HomeworkType(self.type_id).name,
            'datetime_submitted': self.datetime_submitted
        }

        if nest_user:
            # pass
            # TODO: Hit user service
            resp = services.user.get(
                "user/user/{}".format(self.user_id), 
                headers=g.user.headers_dict(),
                params={'nest-students': True}
            )
            if resp.status_code != 200:
                raise CustomError(**resp.json())
            submission_dict['user'] = resp.json()['user']

        if nest_homework:
            submission_dict['homework'] = self.homework.to_dict(has_submitted=True, date_as_string=True)

        if nest_comments:
            submission_dict['comments'] = [c.to_dict(nest_user=True) for c in self.comments]

        return submission_dict


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    user_id = db.Column(db.Integer)
    text = db.Column(db.Text)

    # user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, submission_id, text, user_id):
        self.submission_id = submission_id
        self.text = text
        self.user_id = user_id

    def to_dict(self, nest_user=False):
        dictionary = {
            'id': self.id,
            'submission_id': self.submission_id,
            'text': self.text,
            'user_id': self.user_id
        }

        # TODO: Hit user service
        if nest_user:
            resp = services.user.get(
                "user/user/{}".format(self.user_id), 
                headers=g.user.headers_dict(),
                params={'nest-students': True}
            )
            if resp.status_code != 200:
                raise CustomError(**resp.json())
            dictionary['user'] = resp.json()['user']

        return dictionary
