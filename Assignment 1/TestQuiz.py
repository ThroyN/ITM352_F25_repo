
"""
Testing File for Quiz Application


Test includes:
- Can the program create a questions file when asked?
- Can it load questions from a JSON file?
- Do questions have all the required fields?
- If the questions file is missing, does the code automatically make one?


"""

import json
import os
from QuizzCode import load_questions, create_sample_questions, save_score_history


def test_file_creation():
    """
    PURPOSE:
      Verify the program can create a new questions JSON file.

    DETAILS:
      - I first delete any leftover file from previous runs so this test starts clean.
        I use os.path.exists(path) to check if the file is already on disk.
        If it is, os.remove(path) deletes it, so the next step isn't fooled by old data.
      - Then I call create_sample_questions(file), which should write a valid JSON file.
      - Finally, I assert that os.path.exists(file) is True, meaning the file was actually created.
    """
    print("TEST 1: Can it create a file?")

    test_file = "test_questions.json"

    # Clean up: if a previous run left the file behind, remove it so we test creation for real
    if os.path.exists(test_file):      # checks the filesystem to see if the file path exists
        os.remove(test_file)           # deletes the file.

    # Ask the app to create a fresh questions file
    create_sample_questions(test_file)

    # Validate: the file should now exist on disk
    file_exists = os.path.exists(test_file)

    if file_exists:
        print("  ✓ File created successfully")
        os.remove(test_file)  # Clean up after the test to avoid affecting other tests
        print("✓ PASSED\n")
        return True
    else:
        print("  ✗ FAILED\n")
        return False


def test_loading_questions():
    """
    PURPOSE:
      Make sure load_questions(file) actually reads the JSON and returns a non-empty list.
      - create a fresh test file so I know the JSON is valid.
      - call load_questions(file), which should open the file, json.load it, and return data['questions'].
      - If the returned list has at least one item, I consider that success for this test.
      - I delete the test file at the end to keep the workspace clean.
    """
    print("TEST 2: Can it load questions?")

    test_file = "test_questions.json"

    # Create known-good data to load
    create_sample_questions(test_file)

    # Attempt to load that data
    questions = load_questions(test_file)

    # Basic sanity: did we get any questions at all?
    has_questions = len(questions) > 0

    if has_questions:
        print(f"  ✓ Loaded {len(questions)} questions")
        os.remove(test_file)  # keep the folder tidy between test runs
        print("✓ PASSED\n")
        return True
    else:
        print("  ✗ FAILED\n")
        os.remove(test_file)
        return False


def test_question_structure():
    """
    PURPOSE:
      Verify each question has the expected shape/fields so the quiz can render it.

    FIELDS CHECKED:
      - 'question': the actual text being asked.
      - 'options': a dict mapping labels ('a','b','c','d') → option text.
      - 'correct': which label is correct.
      - 'explanation': a short reason shown after answering.
    """
    print("TEST 3: Do questions have all parts?")

    test_file = "test_questions.json"
    create_sample_questions(test_file)
    questions = load_questions(test_file)

    first_q = questions[0]

    # These flags make it obvious which part failed if something's missing
    has_question = 'question' in first_q
    has_options = 'options' in first_q
    has_correct = 'correct' in first_q
    has_explanation = 'explanation' in first_q

    all_parts_present = has_question and has_options and has_correct and has_explanation

    if all_parts_present:
        print("  ✓ Questions have all required parts")
        os.remove(test_file)
        print("✓ PASSED\n")
        return True
    else:
        print("  ✗ FAILED - missing parts")
        os.remove(test_file)
        return False


def test_score_saving():
    """
    PURPOSE:
      Confirm that save_score_history(...) writes a line to a text file.
      - delete any old history file to avoid mixing results.
      - call save_score_history("TestUser", 4, 5, test_history).
        Internally, that should open the file in append mode ('a') and write one line.
    """
    print("TEST 4: Can it save scores?")

    test_history = "test_history.txt"

    # Clean up any leftover file from a previous test
    if os.path.exists(test_history):
        os.remove(test_history)

    # Write a line to history
    save_score_history("TestUser", 4, 5, test_history)

    # Validate the write happened
    file_created = os.path.exists(test_history)

    if file_created:
        with open(test_history, 'r', encoding='utf-8') as f:
            content = f.read()

        score_saved = "TestUser" in content and "4/5" in content

        if score_saved:
            print("  ✓ Score saved correctly")
            os.remove(test_history)  # cleanup so future runs start clean
            print("✓ PASSED\n")
            return True

    print("  ✗ FAILED")
    if os.path.exists(test_history):
        os.remove(test_history)
    print("✗ FAILED\n")
    return False


def test_auto_create():
    """
    PURPOSE:
      Make sure load_questions(file) can handle a missing file by auto-creating one.

    
      - pick a filename that shouldnt exist and remove it if it somehow does.
      - When I call load_questions(missing_file), our app should catch FileNotFoundError,
        call create_sample_questions(missing_file), and then retry load_questions.
    """
    print("TEST 5: Does it auto-create missing files?")

    test_file = "missing_file.json"

    # Ensure we start from a missing state
    if os.path.exists(test_file):
        os.remove(test_file)

    # Trigger the auto-create + reload behavior
    questions = load_questions(test_file)

    # Validate both creation and content
    file_created = os.path.exists(test_file)
    has_questions = len(questions) >= 5

    if file_created and has_questions:
        print("  ✓ Missing file was created automatically")
        os.remove(test_file)
        print("✓ PASSED\n")
        return True
    else:
        print("  ✗ FAILED")
        if os.path.exists(test_file):
            os.remove(test_file)
        print("✗ FAILED\n")
        return False


def main():
    """
      This function calls each test, counts how many passed, and prints a summary.

   
      - Each test returns True (pass) or False (fail). In Python, True == 1 and False == 0,
        so I can add them to compute the number of passes.
      - I print a divider to make the output easier to scan.
    """
    print("=" * 50)
    print("RUNNING QUIZ TESTS")
    print("=" * 50)
    print()

    # Run each test and collect booleans
    test1 = test_file_creation()
    test2 = test_loading_questions()
    test3 = test_question_structure()
    test4 = test_score_saving()
    test5 = test_auto_create()

    # Count results (True → 1, False → 0)
    total_tests = 5
    passed = test1 + test2 + test3 + test4 + test5
    failed = total_tests - passed

    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}/{total_tests}")
    print(f"Failed: {failed}/{total_tests}")

    if passed == total_tests:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {failed} test(s) failed")

    print("=" * 50)


if __name__ == "__main__":
    main()


