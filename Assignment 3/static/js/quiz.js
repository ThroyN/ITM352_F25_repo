/**
 * quiz.js - Frontend Quiz Logic
 * 
 * Handles all the interactive behavior of the quiz in the browser.
 * Manages displaying questions, checking answers, animations, and talking to Flask server.
 * 
 * AI Usage:
 * - Asked Claude "Create JavaScript for an interactive quiz that fetches questions from a Flask API"
 *   Got the basic structure: fetch questions, display them, handle clicks
 * - Asked Claude "Add green/red animations when user selects correct/incorrect answers with CSS classes"
 *   Got the classList.add approach for correct/incorrect/show-correct classes
 * - I modified the code to work with my specific Flask routes and HTML element IDs
 */

//  Global Variables 
// Track the state of the quiz throughout the session

let questions = [];        // All questions from server
let currentIndex = 0;      // Which question we're on
let score = 0;             // Number of correct answers
let startTime = null;      // When quiz started (for timing)
let breakdown = [];        // Detailed record of each answer
let username = "";         // User's name from input


//  Get References to HTML Elements 
// Grab all the HTML elements we need to update

const introScreen = document.getElementById("intro-screen");
const quizScreen = document.getElementById("quiz-screen");
const resultScreen = document.getElementById("result-screen");

const questionText = document.getElementById("question-text");
const optionsContainer = document.getElementById("options-container");
const feedback = document.getElementById("feedback");
const explanationP = document.getElementById("explanation");
const scoreSpan = document.getElementById("score");
const progressP = document.getElementById("progress");
const finalScoreP = document.getElementById("final-score");
const timeTakenP = document.getElementById("time-taken");
const areasDiv = document.getElementById("areas-for-improvement");


//  Start Button Handler 
// Runs when user clicks "Start Quiz"
// AI Usage: Asked Claude "How do I add a click event listener in JavaScript"
document.getElementById("start-btn").addEventListener("click", async () => {
  username = document.getElementById("username").value.trim();
  const introError = document.getElementById("intro-error");

  // Make sure user entered a name
  if (!username) {
    introError.textContent = "Please enter your name to start.";
    return;
  }

  introError.textContent = "";
  await loadQuestions();
});


/**
 * Fetches quiz questions from the Flask server.
 * 
 * Makes an API call to /api/questions and gets back randomized questions.
 * If successful, switches to quiz screen and shows first question.
 * 
 * AI Usage: Asked Claude "How do I fetch JSON data from a Flask API endpoint"
 *           Got the fetch/await/json pattern and error handling structure
 */
async function loadQuestions() {
  try {
    const res = await fetch("/api/questions");
    const data = await res.json();
    
    if (data.status !== "ok") {
      throw new Error(data.message || "Failed to load questions");
    }

    // Set up quiz with loaded questions
    questions = data.questions;
    currentIndex = 0;
    score = 0;
    breakdown = [];
    startTime = Date.now();  // I added this for timing

    // Switch screens
    introScreen.classList.add("hidden");
    quizScreen.classList.remove("hidden");

    showQuestion();
    
  } catch (err) {
    alert("Error loading questions: " + err.message);
  }
}


/**
 * Displays the current question and creates answer buttons.
 * 
 * Updates the HTML to show question text and dynamically creates
 * clickable buttons for each answer option.
 * 
 * AI Usage: Asked Claude "How do I dynamically create HTML buttons in JavaScript"
 *           Got the createElement and appendChild approach
 *           I modified it to match my button structure and add dataset.label
 */
function showQuestion() {
  const q = questions[currentIndex];

  // Clear previous question stuff
  feedback.textContent = "";
  explanationP.textContent = "";
  
  // Update progress text
  progressP.textContent = `Question ${currentIndex + 1} of ${questions.length}`;
  questionText.textContent = q.question;

  // Clear old buttons and create new ones
  optionsContainer.innerHTML = "";
  
  q.options.forEach(opt => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.textContent = `${opt.label}) ${opt.text}`;
    btn.dataset.label = opt.label;  // Store label for checking answer
    btn.onclick = () => handleAnswer(btn, opt.label);
    optionsContainer.appendChild(btn);
  });
}


/**
 * Handles what happens when user clicks an answer.
 * 
 * Checks if answer is correct, adds animation classes (green/red),
 * updates score, and shows explanation.
 * 
 * @param {HTMLElement} clickedButton - The button that was clicked
 * @param {string} selectedLabel - The answer letter ("a", "b", "c", or "d")
 * 
 * AI Usage: Asked Claude "How do I add CSS animations to show correct/incorrect answers"
 *           Got the approach of adding "correct" and "incorrect" classes
 *           Also suggested highlighting correct answer when user is wrong
 *           I integrated this with my score tracking and breakdown array
 */
function handleAnswer(clickedButton, selectedLabel) {
  const q = questions[currentIndex];
  const correct = selectedLabel === q.correct_label;
  const allButtons = document.querySelectorAll(".option-btn");

  // Save answer details for review later (I added this breakdown tracking)
  breakdown.push({
    questionId: q.id,
    question: q.question,
    selectedLabel,
    correctLabel: q.correct_label,
    correct,
    explanation: q.explanation
  });

  // Show visual feedback
  if (correct) {
    clickedButton.classList.add("correct");  // Green animation
    score++;
    feedback.textContent = "✓ Correct!";
    feedback.style.color = "#4CAF50";
  } else {
    clickedButton.classList.add("incorrect");  // Red animation
    feedback.textContent = `✗ Incorrect. The correct answer was '${q.correct_label}'.`;
    feedback.style.color = "#f44336";
    
    // Highlight correct answer
    allButtons.forEach(btn => {
      if (btn.dataset.label === q.correct_label) {
        btn.classList.add("show-correct");
      }
    });
  }

  // Show explanation
  explanationP.textContent = "Explanation: " + (q.explanation || "");
  explanationP.style.display = "block";
  scoreSpan.textContent = score;

  // Disable all buttons
  allButtons.forEach(btn => (btn.disabled = true));
}


// Next Button Handler 
// Goes to next question or shows results if done
document.getElementById("next-btn").addEventListener("click", () => {
  if (currentIndex < questions.length - 1) {
    currentIndex++;
    showQuestion();
  } else {
    finishQuiz();
  }
});


/**
 * Shows final results and saves score to server.
 * 
 * Calculates time taken, displays final score and percentage,
 * shows missed questions for review, and sends data to Flask to save.
 * 
 * AI Usage: Asked Claude "How do I calculate time elapsed in JavaScript"
 *           Got the Date.now() approach and Math.round for seconds
 *           Asked "How do I send POST request with JSON to Flask"
 *           Got the fetch POST pattern with headers and body
 *           
 */
async function finishQuiz() {
  // Calculate quiz duration
  const endTime = Date.now();
  const timeTakenSec = Math.round((endTime - startTime) / 1000);

  // Switch to results screen
  quizScreen.classList.add("hidden");
  resultScreen.classList.remove("hidden");

  // Show final score
  const percent = ((score / questions.length) * 100).toFixed(1);
  finalScoreP.textContent = `${username}, your final score: ${score}/${questions.length} (${percent}%)`;
  timeTakenP.textContent = `Time taken: ${timeTakenSec} seconds.`;

  // Show missed questions for review
  const missed = breakdown.filter(b => !b.correct);
  if (missed.length === 0) {
    areasDiv.innerHTML = "<p>Perfect score! Excellent work! 🎉</p>";
  } else {
    let html = "<h3>Questions to review:</h3>";
    missed.forEach(m => {
      html += `<p><strong>${m.question}</strong><br>
        Your answer: ${m.selectedLabel}<br>
        Correct answer: ${m.correctLabel}<br>
        Explanation: ${m.explanation}</p>`;
    });
    areasDiv.innerHTML = html;
  }

  // Send score to server
  try {
    await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        correct: score,
        total: questions.length,
        timeTaken: timeTakenSec,
        breakdown
      })
    });
  } catch (err) {
    console.error("Failed to save score:", err);
  }
}