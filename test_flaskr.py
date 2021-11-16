import json
import os
import unittest

from dotenv import find_dotenv, load_dotenv
from flask_sqlalchemy import SQLAlchemy

from flaskr import app
from models import Question, setup_db

# Load environment variables from .env
load_dotenv(find_dotenv())

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

ADMIN_TOKEN = os.environ.get("TEST_ADMIN_TOKEN")
PLAYER_TOKEN = os.environ.get("TEST_PLAYER_TOKEN")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        setup_db(self.app, TEST_DATABASE_URL, False)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            "question": "Which country has largest population in the world?",
            "answer": "China",
            "difficulty": "3",
            "category": "2"
        }

        self.admin_headers = {
            'Authorization': 'Bearer {}'.format(ADMIN_TOKEN)
        }

        self.player_headers = {
            'Authorization': 'Bearer {}'.format(PLAYER_TOKEN)
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question,
                                 headers=self.admin_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])

    def test_422_if_question_answer_is_missing(self):
        data = self.new_question
        del data['answer']
        res = self.client().post("/questions", json=self.new_question,
                                 headers=self.admin_headers)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_question(self):
        question_id = Question.query.first().id  # to avoid 404 on re running tests
        res = self.client().delete(
            f"/questions/{question_id}", headers=self.admin_headers)
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], str(question_id))

        self.assertEqual(question, None)

    def test_search_questions(self):
        res = self.client().post(
            '/questions/search', json={'searchTerm': 'Which'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'], len(data['questions']))
        self.assertEqual(data['current_category'], None)

    def test_get_questions_by_category(self):
        category_id = 4
        res = self.client().get(f"/categories/{category_id}/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["current_category"], category_id)

    def test_422_if_search_term_missing(self):
        res = self.client().post('/questions', json={}, headers=self.admin_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_play_quiz_game(self):
        previous_questions = [5, 7]
        res = self.client().post('/quizzes',
                                 json={
                                     'previous_questions': previous_questions,
                                     'quiz_category':
                                     {'type': None, 'id': None}
                                 },
                                 headers=self.player_headers
                                 )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertFalse(data['question']['id'] in previous_questions)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
