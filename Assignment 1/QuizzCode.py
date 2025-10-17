"""
A multiple choice quiz that reads questions from a file,
this quiz checks to see if input is valid and tracks the score by exporting it to a txt file.
"""

import json
import datetime


def load_questions(filename="quiz_questions.json"):
    """
    Reads the file with the questions from the .json file.
    Handels if the file isnt found if the path is wrong for example it will throw an error message.
    If file isnt found it will create a new .json that has questions by calling the file create_sample_questions.

    Argument:
        filename (str): Path to the JSON file containing questions

    Returns:
        list: List of question dictionaries
    """
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['questions']
    except FileNotFoundError:
        print(f"Error:a {filename} not found. Creating sample file...")
        create_sample_questions(filename)
        return load_questions(filename)



def create_sample_questions(filename="quiz_questions.json"):
    """
    Create a sample quiz questions file if none exists.
    
    ArgumentsL
        filename (str): Path where the sample file should be created
    """
    sample_data = {
        "questions": [
            {
                "question": "What is the capital of France?",
                "options": {
                    "a": "London",
                    "b": "Berlin",
                    "c": "Paris",
                    "d": "Madrid"
                },
                "correct": "c",
                "explanation": "Paris is the capital and largest city of France."
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": {
                    "a": "Venus",
                    "b": "Mars",
                    "c": "Jupiter",
                    "d": "Saturn"
                },
                "correct": "b",
                "explanation": "Mars is called the Red Planet because of rust on its surface, which gives it a reddish appearance."
            },
            {
                "question": "What is the largest ocean on Earth?",
                "options": {
                    "a": "Atlantic Ocean",
                    "b": "Indian Ocean",
                    "c": "Arctic Ocean",
                    "d": "Pacific Ocean"
                },
                "correct": "d",
                "explanation": "The Pacific Ocean is the largest and deepest ocean, covering approximately 63 million square miles."
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "options": {
                    "a": "Charles Dickens",
                    "b": "William Shakespeare",
                    "c": "Jane Austen",
                    "d": "Mark Twain"
                },
                "correct": "b",
                "explanation": "William Shakespeare wrote 'Romeo and Juliet' around 1594-1596."
            },
            {
                "question": "What is the chemical symbol for gold?",
                "options": {
                    "a": "Go",
                    "b": "Gd",
                    "c": "Au",
                    "d": "Ag"
                },
                "correct": "c",
                "explanation": "The symbol Au is gold, I know because of chemistry'"
            }
        ]
    }
    
    with open(filename, 'w') as file:
        json.dump(sample_data, file, indent=4)
    print(f"Sample questions file created: {filename}")
"""
This part of the code opens or creates a new file using the name stored in “filename”.
The 'w' means write mode, which replaces anything already in the file.
Then it writes the quiz questions (sample_data) into that file in JSON format.
After that, it prints a message saying the sample questions file was created successfully.
"""


def get_valid_answer(valid_options):
    """
This loop keeps running until the user gives a valid answer.
It asks the user to type their answer, removes any extra spaces before or after what they type using .strip(),
and changes it to lowercase so the input is easier to check. Without the strip method, spaces would count as input from the user which is something we do not want.
Then it checks if the answer is one of the valid options.
If it is, the function returns that answer and stops the loop.
If not, it shows a message telling the user to enter a valid choice and asks again.
"""
    while True:
        answer = input("Your answer: ").strip().lower()
        if answer in valid_options:
            return answer
        else:
            print(f"Invalid input. Please enter one of: {', '.join(valid_options)}")


def save_score_history(username, score, total, filename="score_history.txt"):
    """
 This function saves the players quiz results to a text file.
It takes the players name, score, and total number of questions to calculate their percentage.
It also adds the current date and time so you know when the quiz was taken.
The file is opened in 'a' mode, which means it adds the new score to the end instead of replacing old ones.
Then it writes everything in a clean format and prints a message saying the score was saved.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    percentage = (score / total) * 100
    
    with open(filename, 'a') as file:
        file.write(f"{timestamp} | {username} | Score: {score}/{total} ({percentage:.1f}%)\n")
    
    print(f"\nScore saved to {filename}")


def run_quiz():
    """
    Main function to run the interactive quiz.
    Loads questions, presents them to the user, tracks score,
    and saves results to history.
    """
    print("=" * 50)
    print("Welcome to the Interactive Quiz!")
    print("=" * 50)
    
    # Get user's name
    username = input("\nEnter your name: ").strip()
    if not username:
        username = "Anonymous"
    #Strip method used again to prevent uses of spaces
    # Load questions from file
    questions = load_questions()
    
    if len(questions) < 5:
        print("Warning: Quiz should have at least 5 questions!")
    #Checks to see if questions are more than 5 if not it will throw a warning message.cle
    score = 0
    total_questions = len(questions)
    
    print(f"\nLet's begin! You'll be asked {total_questions} questions.")
    print("Enter the letter (a, b, c, or d) of your answer.\n")
    
    # Loop through each question
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i} of {total_questions}:")
        print(q['question'])
        print()
        
        # Display options
        for key, value in sorted(q['options'].items()):
            print(f"  {key}) {value}")
        print()
        
        # Get valid answer from user
        valid_options = list(q['options'].keys())
        user_answer = get_valid_answer(valid_options)
        
        # Check if answer is correct
        if user_answer == q['correct']:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Incorrect. The correct answer was '{q['correct']}'.")
        
        # Show explanation
        print(f"Explanation: {q['explanation']}")
        print("-" * 50)
    
    # Display final results
    percentage = (score / total_questions) * 100
    print("\n" + "=" * 50)
    print("QUIZ COMPLETED!")
    print("=" * 50)
    print(f"\n{username}, your final score: {score}/{total_questions} ({percentage:.1f}%)")
    
    # Provide feedback based on score
    if percentage == 100:
        print("Perfect score.")
    elif percentage >= 80:
        print(" Pretty good")
    elif percentage >= 60:
        print("Get to studying")
    else:
        print("Skill issue")
    
    # Save score to history file
    save_score_history(username, score, total_questions)
    print("\nThank you for playing!")


# Run the quiz when the script is executed
if __name__ == "__main__":
    run_quiz()