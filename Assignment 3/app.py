"""
app.py - Flask Web Server for Quiz Application

This is the main file that runs the web server for the quiz app.
It handles HTTP requests from the browser and sends back responses.

AI Usage:
- Basic Flask structure generated using Claude with prompt:
 "Create a Flask app with routes for serving quiz questions and saving scores"
- Question shuffling logic suggested by Claude
- I modified the routes to match my frontend JavaScript requirements
- Added error handling and validation myself

How to run:
python app.py
Then visit: http://127.0.0.1:5000 in your browser
"""

from flask import Flask, render_template, jsonify, request
import random
from quiz_core import load_questions, save_score_history

# Create Flask application instance
app = Flask(__name__)


def prepare_questions_for_api():
    """
    Loads questions and prepares them to be sent to the frontend.
    
    This function does three important things:
    1. Loads questions from the JSON file using quiz_core.py
    2. Randomizes the order of questions (so each quiz is different)
    3. Randomizes the order of answer options (prevents memorizing positions)
    
    The frontend JavaScript will receive this formatted data and display
    the questions one at a time to the user.
    
    
    AI Usage: Randomization logic suggested by Claude with prompt:
    "How do I shuffle both questions and their answer options in Python?"
    """
    # Load questions from the JSON file
    raw_questions = load_questions()
    
    # Shuffle questions so they appear in random order each time
    random.shuffle(raw_questions)
    
    # Prepare questions in a format the frontend expects
    prepared = []
    for idx, q in enumerate(raw_questions, start=1):
        # Convert options dictionary {"a": "Paris", "b": "London"...}
        # into a list of tuples [("a", "Paris"), ("b", "London")...]
        options_items = list(q["options"].items())
        
        # Shuffle the answer options so "a" isn't always the same position
        random.shuffle(options_items)
        
        # Build the question object
        prepared.append({
            "id": idx,
            "question": q["question"],
            # Convert to list of label/text dictionaries for easy frontend use
            "options": [
                {"label": label, "text": text}
                for label, text in options_items
            ],
            "correct_label": q["correct"],  # Still send correct answer (for now)
            "explanation": q.get("explanation", "")
        })
    
    return prepared


@app.route("/")
def index():
    """
    Home page route - serves the main quiz HTML page.
    
    When someone visits http://127.0.0.1:5000, Flask runs this function.
    It tells Flask to render the index.html template and send it to the browser.
    
    Returns:
        HTML page (from templates/index.html)
    
    AI Usage: Asked Claude "How do I create a Flask route that serves an HTML page".
    """
    return render_template("index.html")


@app.route("/api/questions")
def api_questions():
    """
    API endpoint that sends quiz questions to the frontend as JSON.
    
    The JavaScript code calls this route with:
        fetch("/api/questions")
    
    This prepares the questions and sends them back in JSON format.
    The frontend then displays them one at a time.
    
    AI Usage: "How do I create a Flask API endpoint that returns JSON data"
              Error handling try/except pattern suggested by Claude"
    """
    try:
        # Get prepared questions with randomized order
        questions = prepare_questions_for_api()
        # Send back as JSON with success status
        return jsonify({"status": "ok", "questions": questions})
    except Exception as e:
        # If something goes wrong, send error message
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/score", methods=["POST"])
def api_score():
    """
    API endpoint that receives and saves quiz scores from the frontend.
    
    The JavaScript sends quiz results here after the user finishes:
    fetch("/api/score", {method: "POST", body: JSON...})
    
    This function receives the score data and saves it to score_history.json
    using the save_score_history function from quiz_core.py.
    
    
    AI Usage: "How do I create a Flask POST endpoint that receives JSON data"
              Basic POST handler pattern from Claude, I added the validation checks myself."
    """
    # Get JSON data from the request body
    # force=True allows parsing even without proper Content-Type header
    data = request.get_json(force=True)
    
    # Extract the data fields
    username = data.get("username", "Anonymous")
    correct = data.get("correct")
    total = data.get("total")
    time_taken = data.get("timeTaken")
    breakdown = data.get("breakdown", [])
    
    # Validate that required fields are present
    if correct is None or total is None:
        return jsonify({
            "status": "error", 
            "message": "Missing score fields"
        }), 400
    
    # Save the score to the JSON file
    try:
        save_score_history(username, correct, total, time_taken, breakdown)
        return jsonify({"status": "ok"})
    except Exception as e:
        # If saving fails, send error message
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500


# This runs only if you execute this file directly (python app.py)
# Not if it's imported as a module
if __name__ == "__main__":
    app.run(debug=True)