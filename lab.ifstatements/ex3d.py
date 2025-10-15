def determine_progress_no_if(hits, spins):
    # 0: On your way!, 1: Almost there!, 2: You win!, 3: Get going!
    messages = ["On your way!", "Almost there!", "You win!", "Get going!"]

    # Safe ratio (avoid div-by-zero); will be overridden if spins==0
    ratio = hits / (spins or 1)

    # Booleans become ints: False -> 0, True -> 1
    get_going = (spins == 0) or (ratio <= 0)             # needs "Get going!"
    almost    = (ratio >= 0.25)                          # at least "Almost there!"
    win       = (ratio >= 0.5) and (hits < spins)        # upgrade to "You win!"

    # Base tier: 0 (On your way!); bump by almost/win
    idx = 0 + almost + win                               # 0, 1, or 2

    # Override with "Get going!" when needed
    idx = get_going * 3 + (1 - get_going) * idx

    return messages[idx]

