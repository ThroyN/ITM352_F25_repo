items = ("hello", 10, "goodbye", 3, "goodnight", 5)
user_input = input("Enter a value to append: ")

try:
    items.append(user_input)   # this will fail
except Exception as e:
    print(f"Error: Cannot append to tuple. Details: {e}")

