def count_strings(items):
    """Return how many elements in the tuple/list are strings."""
    string_count = 0
    for element in items:
        if isinstance(element, str):
            string_count += 1
    return string_count


def test_count_strings():
    # Test case 1: mix of strings and numbers
    assert count_strings(("hello", 10, "goodbye", 3, "goodnight", 5)) == 3
    
    # Test case 2: all strings
    assert count_strings(("a", "b", "c")) == 3
    
    # Test case 3: all numbers
    assert count_strings((1, 2, 3, 4)) == 0
    
    # Test case 4: empty tuple
    assert count_strings(()) == 0
    
    # Test case 5: mixed types
    assert count_strings((True, "yes", None, "no")) == 2
    
    print("All test cases passed!")

# Run the test function
test_count_strings()
