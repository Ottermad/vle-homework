import datetime
from enum import Enum

from app import db


class HomeworkType(Enum):
    HOMEWORK = 0
    ESSAY = 1
    QUIZ = 2


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name
