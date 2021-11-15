import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from sqlalchemy.sql.expression import func

from models import Category, Question, setup_db

from .auth import AuthError, requires_auth

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    """
    helper function for pagination
    """
    page = request.args.get("page", 1, type=int)
    offset = (page-1) * QUESTIONS_PER_PAGE

    query = selection.offset(offset).limit(QUESTIONS_PER_PAGE).all()
    questions = [question.format() for question in query]

    return questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # CORS(app, resources={r"*/api/*" : {origins: '*'}})
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        return response

    @app.route('/categories')
    def retrieve_categories():
        """
        Create an endpoint to handle GET requests
        for all available categories.
        """
        categories = Category.query.order_by(Category.type).all()
        categories = {category.id: category.type for category in categories}

        if len(categories) == 0:
            abort(404)

        return jsonify({'success': True, 'categories': categories})

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        """
        Create a GET endpoint to get questions based on category.
        """

        try:
            questions = Question.query.filter(
                Question.category == str(category_id)
            ).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except Exception as ex:
            print(str(ex))
            abort(422)

    @app.route("/questions")
    def retrieve_questions():
        """
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.
        """

        selection = Question.query.order_by(Question.id)
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.type).all()
        categories = {category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": selection.count(),
            "categories": categories,
            "current_category": None
        })

    @app.route("/questions/<question_id>", methods=['DELETE'])
    @requires_auth('delete:question')
    def delete_question(token, question_id):
        """
        Create an endpoint to DELETE question using a question ID.
        """
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            return jsonify({'success': True, 'deleted': question_id})

        except Exception as ex:
            print(str(ex))
            abort(422)

    @app.route("/questions", methods=['POST'])
    @requires_auth('add:question')
    def add_question(token):
        """
        Create an endpoint to POST a new question,
        which will require the question and answer text,
        category, and difficulty score.
        """
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        if not (new_question and new_answer and new_difficulty and new_category):
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                difficulty=new_difficulty,
                category=new_category
            )
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
            })

        except Exception as ex:
            print(str(ex))
            abort(422)

    @app.route('/questions/<int:question_id>', methods=['PATCH'])
    @requires_auth('update:question')
    def edit_question(token, question_id):
        """
        Create an endpoint to edit a  question,
        which will require the question_id, category, and difficulty score.
        """

        try:
            question = Question.query.filter_by(id=question_id).first()
            if not question:
                abort(404)

            question_data = request.get_json()

            for key, value in question_data.items():
                setattr(question, key, value)
            question.update()

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except Exception as ex:
            print(str(ex))
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """
        Create a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term
        is a substring of the question.
        """
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if not search_term:
            abort(422)

        search_results = Question.query.order_by(Question.id).filter(
            Question.question.ilike(f'%{search_term}%')
        ).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in search_results],
            'total_questions': len(search_results),
            'current_category': None
        })

    @app.route('/quizzes', methods=['POST'])
    @requires_auth('play:quiz')
    def play_quiz(token):
        """
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.
        """

        try:
            body = request.get_json()

            quiz_category = body.get('quiz_category', None)
            category_type = quiz_category['type']
            category_id = quiz_category['id']

            previous_questions = body.get('previous_questions', None)
            previous_questions = Question.id.notin_((previous_questions))

            if category_type:
                new_question = Question.query.filter(previous_questions).filter_by(
                    category=category_id).order_by(func.random()).first()
            else:
                new_question = Question.query.filter(
                    previous_questions).order_by(func.random()).first()

            print(new_question)

            return jsonify({'success': True, 'question': new_question.format()})
        except Exception as ex:
            print("Error occurred while fetching question", str(ex))
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
            }),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
            }),
            422,
        )

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app
