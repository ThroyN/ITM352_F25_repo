def determine_progress2(hits, spins):
    if spins == 0:
        return "Get going!"

    ratio = hits / spins

    if ratio <= 0:
        return "Get going!"

    if ratio >= 0.5 and hits < spins:
        return "You win!"

    if ratio >= 0.25:
        return "Almost there!"

    return "On your way!"


def test_determine_progress(progress_function):
    assert progress_function(10, 0) == "Get going!"      # spins == 0
    assert progress_function(1, 10) == "On your way!"    # 0 < ratio < 0.25
    assert progress_function(3, 10) == "Almost there!"   # 0.25 ≤ ratio < 0.5
    assert progress_function(6, 10) == "You win!"        # ratio ≥ 0.5, hits < spins
    assert progress_function(0, 5)  == "Get going!"      # ratio == 0

test_determine_progress(determine_progress2)
print("All tests passed!")
