def test_determine_progress(progress_function):
    # Test case 1: spins = 0 → "Get going!"
    assert progress_function(10, 0) == "Get going!", "Test case 1 failed"

    # Test case 2: ratio > 0 but less than 0.25 → "On your way!"
    assert progress_function(1, 10) == "On your way!", "Test case 2 failed"

    # Test case 3: ratio >= 0.25 but less than 0.5 → "Almost there!"
    assert progress_function(3, 10) == "Almost there!", "Test case 3 failed"

    # Test case 4: ratio >= 0.5 but hits < spins → "You win!"
    assert progress_function(6, 10) == "You win!", "Test case 4 failed"

    # Test case 5: hits = 0 and spins > 0 → ratio = 0 → "Get going!"
    assert progress_function(0, 5) == "Get going!", "Test case 5 failed"

    print("All test cases passed!")

