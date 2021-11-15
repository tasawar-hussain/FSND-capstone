import os

from dotenv import find_dotenv, load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

# Load environment variables from .env
load_dotenv(find_dotenv())

# Connect to the database
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
FLASK_APP = os.environ.get("FLASK_APP")
FLASK_ENV = os.environ.get("FLASK_ENV")


db = SQLAlchemy()
'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=SQLALCHEMY_DATABASE_URL):
    app.config["SQLALCHEMY_DATABASE_URL"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SQLALCHEMY_ECHO"] = SQLALCHEMY_ECHO
    app.config['FLASK_APP'] = FLASK_APP
    app.config['FLASK_ENV'] = FLASK_ENV
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {'id': self.id, 'type': self.type}
