def isLeapYear(year):
    if year % 400 == 0:
        return "Leap year"
    if year % 100 == 0:
        return "Not a leap year"
    if year % 4 == 0:
        return "Leap year"
    return "Not a leap year"


def is_leap(year: int) -> bool:
    # A: divisible by 4
    # B: not divisible by 100
    # C: divisible by 400
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
assert is_leap(1996)      # True: divisible by 4 and not 100
assert not is_leap(1900)  # False: divisible by 100 but not 400
assert is_leap(2000)      # True: divisible by 400
assert not is_leap(2023)  # False
assert is_leap(2024)      # True

print("Base leap-year tests passed.")
