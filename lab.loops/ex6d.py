items = ("hello", 10, "goodbye", 3, "goodnight", 5)
user_input = input("Enter a value to append: ")

try:
    items.append(user_input)   # will cause error
except Exception:
    # Instead of error, create new tuple and reassign
    items = items + (user_input,)

print("Appended tuple:", items)
