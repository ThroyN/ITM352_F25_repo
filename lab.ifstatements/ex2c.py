test_cases = [
    [],                       # 0 elements
    [1, 2, 3, 4],             # 4 elements (fewer than 5)
    [1, 2, 3, 4, 5],          # 5 elements (between 5 and 10)
    [1, 2, 3, 4, 5, 6, 7],    # 7 elements (between 5 and 10)
    list(range(10)),          # 10 elements (between 5 and 10)
    list(range(15))           # 15 elements (more than 10)
]


for case in test_cases:
    print(f"Testing list of length {len(case)}: ", end="")
    if len(case) < 5:
        print("The list has fewer than 5 elements.")
    elif 5 <= len(case) <= 10:
        print("The list has between 5 and 10 elements.")
    else:
        print("The list has more than 10 elements.")
