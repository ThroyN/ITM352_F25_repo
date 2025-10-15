def is_leap(year: int) -> bool:
    # A: divisible by 4
    # B: not divisible by 100
    # C: divisible by 400
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)



assert is_leap(1996)  # true: /4 and not /100
assert not is_leap(1900)  # false: /100 but not /400
assert is_leap(2000)  # true: /400
assert not is_leap(2023)
assert is_leap(2024)

print("Base leap-year tests passed.")
