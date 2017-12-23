from app import db
from app.homework.models import Homework, HomeworkType, Submission


class Essay(Homework):
    id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.ESSAY.value
    }

    def __init__(self, lesson_id, title, description, date_due):
        super().__init__(lesson_id, title,description, HomeworkType.ESSAY.value, date_due)


class EssaySubmission(Submission):
    id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    text = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.ESSAY.value,
    }

    def __init__(self, homework_id, user_id, datetime_submitted, text):
        super().__init__(homework_id, HomeworkType.ESSAY.value, user_id, datetime_submitted)
        self.text = text

    def to_dict(self, **kwargs):
        submission_dict = super().to_dict(**kwargs)
        submission_dict['text'] = self.text
        return submission_dict
