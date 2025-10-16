import random

reqs = [
    "Write the history of scores out to a file.",
    "Notify the user when they get a new high score.",
    "Allow for multiple numbers of answers to a question.",
    "Allow for multiple correct answers.",
    "Allow the user to choose a category for their questions, e.g. history, art, modern politics, NBA trivia, NFL trivia, music trivia, etc.",
    "Allow an option to provide a hint.",
    "Add explanations for why the correct answer is the correct answer.",
    "Create a separate application that interactively asks for questions and answers and stores them in the proper JSON format.",
    "Add a timer for each question and give bonus points for the fastest correct quiz answers or total quiz time.",
    "Add a 50/50 feature (eliminating 2 of the 4 answers, wrong ones that is) that can only be used once per game instance."
]

R1, R2 = random.sample(reqs, 2)
print("R1:", R1)
print("R2:", R2)