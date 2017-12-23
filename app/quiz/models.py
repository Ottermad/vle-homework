from app import db
from app.homework.models import Homework, HomeworkType, Submission


class Quiz(Homework):
    id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)
    number_of_questions = db.Column(db.Integer)

    questions = db.relationship('Question', backref='quiz', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.QUIZ.value,
    }

    def __init__(self, lesson_id, title, description, date_due, number_of_questions):
        super().__init__(lesson_id, title, description, HomeworkType.QUIZ.value, date_due)
        self.number_of_questions = number_of_questions

    def to_dict(self, date_as_string=False, nest_lesson=False, has_submitted=False, user_id=None):
        dictionary = super().to_dict(date_as_string, nest_lesson, has_submitted, user_id)
        dictionary['number_of_questions'] = self.number_of_questions
        dictionary['questions'] = [q.to_dict() for q in self.questions]
        return dictionary


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    question_text = db.Column(db.String(120))
    question_answer = db.Column(db.String(120))

    def __init__(self, homework_id, question_text, question_answer):
        self.homework_id = homework_id
        self.question_answer = question_answer
        self.question_text = question_text

    def to_dict(self):
        return {
            'homework_id': self.homework_id,
            'question_text': self.question_text,
            'answer': self.question_answer,
            'id': self.id
        }


class QuizAnswer(db.Model):
    __table_args__ = (
        db.UniqueConstraint("submission_id", "question_id"),
    )
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(120))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    correct = db.Column(db.Boolean)

    def __init__(self, answer, submission_id, question_id):
        self.answer = answer
        self.submission_id = submission_id
        self.question_id = question_id

    def to_dict(self):
        return {
            'answer': self.answer,
            'id': self.id,
            'submission_id': self.submission_id,
            'question_id': self.question_id,
            'correct': self.correct
        }


class QuizSubmission(Submission):
    id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    total_score = db.Column(db.Integer)

    answers = db.relationship(QuizAnswer, backref='submission', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.QUIZ.value,
    }

    def __init__(self, homework_id, user_id, datetime_submitted):
        super().__init__(homework_id, HomeworkType.QUIZ.value, user_id, datetime_submitted)
        self.total_score = 0

    def mark(self):
        score = 0
        # TODO: Refactor to make more efficient
        for answer in self.answers:
            answer.correct = False
            question = Question.query.get(answer.question_id)
            if question.question_answer == answer.answer:
                score += 1
                answer.correct = True
        self.total_score = score

    def to_dict(self, **kwargs):
        submission_dict = super().to_dict(**kwargs)
        submission_dict['score'] = self.total_score
        submission_dict['answers'] = [answer.to_dict() for answer in self.answers]
        return submission_dict
