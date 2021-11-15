## Capstone - Trivia with Authorization

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where you come in! Help them finish the trivia app so they can start holding trivia and seeing who's the most knowledgeable of the bunch. The application must:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

Completing this trivia app will give you the ability to structure plan, implement, and test an API - skills essential for enabling your future applications to communicate with others.

## Getting Started - Setup

### Installing Dependencies
- [Python >= v3.8](https://www.python.org/)
- [pip >= 21.1](https://pypi.org/project/pip/)
- [PostgreSQL >= v10](https://www.postgresql.org/)

#### Frontend Dependencies
Change current working directory to `.frontend` and the run below command to install dependencies
```
npm install
```

#### Backend Dependencies

Change current working directory to `/backend`, activate virtual environment and the run below command to install dependencies
```
pip install -r requirements.txt
```

## Running the Backend Server (API)
First setup the database, With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```
psql trivia < trivia.psql
```

To run the server, will be accessible on (`http://127.0.0.1:5000/`), execute below command:
```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run --reload
```

Setting the `FLASK_ENV` variable to `development` abd --reload flag will detect file changes and restart the server automatically.
Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory.

## Running the Frontend

Run the below command to start the frontend server. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.
```
npm start
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
Omit the dropdb command the first time you run tests.
All tests are kept in that file and should be maintained as updates are made to app functionality.

## API Reference

### Getting Started
**Base URL**: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, http://127.0.0.1:5000/, which is set as a proxy in the frontend(`http://127.0.0.1:3000/`) configuration.
**Authentication**: This version of the application does not require authentication or API keys.

### Error Handling

Errors are returned as JSON in the following format:<br>

  ```json
    {
        "success": False,
        "error": 404,
        "message": "resource not found"
    }
  ```

The API will return three types of errors:

* 400 – bad request
* 404 – resource not found
* 422 – unprocessable
* 500 - internal server error

### Endpoints

#### GET /categories

* General: Returns a list categories.
* Sample: `curl http://127.0.0.1:5000/categories`<br>

  ```json
        {
            "categories": {
                "1": "Science",
                "2": "Art",
                "3": "Geography",
                "4": "History",
                "5": "Entertainment",
                "6": "Sports"
            },
            "success": true
        }
  ```

#### GET /questions

* General:
  * Returns a list questions.
  * Results are paginated in groups of 10.
  * Also returns list of categories and total number of questions.
* Sample: `curl http://127.0.0.1:5000/questions`<br>

  ```json
        {
            "categories": {
                "1": "Science",
                "2": "Art",
                "3": "Geography",
                "4": "History",
                "5": "Entertainment",
                "6": "Sports"
            },
            "questions": [
                {
                    "answer": "Tom Cruise",
                    "category": 5,
                    "difficulty": 4,
                    "id": 4,
                    "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
                },
             ...


            ],
            "success": true,
            "total_questions": 10
        }
  ```
#### DELETE /questions/\<int:id\>

* General:
  * Deletes the book of the given ID if it exists. Returns the id of the deleted book, success value
* Sample: `curl  -X DELETE http://127.0.0.1:5000/questions/1`<br>

  ```json
        {
            "deleted": 1,
            "success": true
        }
  ```
#### POST /questions

* General:
  * Creates a new question using the submitted question, answer, difficlulty and category id.
  * Returns the id of the created question, question id, answer, success value, and total question
* Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{
            "question": "Which team would win Cricket T20 2021 worldcup?",
            "answer": "Pakistan",
            "difficulty": 4,
            "category": "5"
        }'`

  ```json
        {
            "created": 21,
            "question_created": "Which team would win Cricket T20 2021 worldcup?",
            "questions": [
                {
                    "answer": "Pakistan",
                    "category": 5,
                    "difficulty": 4,
                    "id": 2,
                    "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
                },
            ],
            "success": true,
            "total_questions": 21
        }
  ```
#### GET /categories/\<int:id\>/questions

* General:
  * Gets questions by category id .
  * Returns current_category, questions, success, and total_questions.
* Sample: `curl http://127.0.0.1:5000/categories/3/questions`<br>
  ```json
        {
            "current_category": 3,
            "questions": [
            {
              "answer": "Lake Victoria",
              "category": 3,
              "difficulty": 2,
              "id": 13,
              "question": "What is the largest lake in Africa?"
            },
            {
              "answer": "The Palace of Versailles",
              "category": 3,
              "difficulty": 3,
              "id": 14,
              "question": "In which royal palace would you find the Hall of Mirrors?"
            },
            {
              "answer": "Agra",
              "category": 3,
              "difficulty": 2,
              "id": 15,
              "question": "The Taj Mahal is located in which Indian city?"
            }
          ],
          "success": true,
          "total_questions": 3
        }
  ```
#### POST /quizzes

* General:
  * Allows users to play the quiz game of any or all category
  * Returns success and random question not among previous questions.
  * Sample: `curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions": [4], "quiz_category": {"type": "History", "id": "4"}}'`<br>

  ```json
        {
            "question": {
                "answer": "George Washington Carver",
                "category": 4,
                "difficulty": 2,
                "id": 12,
                "question": "Who invented Peanut Butter?"
            },
            "success": true
        }
  ```

## Roles Reference
### Admin

Can add/update/delete question

Permissions:

- `add:question`
- `edit:question`
- `delete:question`

### Player

Can play quiz

Permissions:

- `play:quiz`
## Authors

[Tasawar Hussain](https://github.com/tasawar-hussain)
