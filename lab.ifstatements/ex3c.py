def determine_progress3(hits, spins):
    if spins == 0:
        return "Get going!"
    ratio = hits / spins
    if ratio <= 0:
        return "Get going!"
    elif ratio >= 0.5 and hits < spins:
        return "You win!"
    elif ratio >= 0.25:
        return "Almost there!"
    else:
        return "On your way!"
