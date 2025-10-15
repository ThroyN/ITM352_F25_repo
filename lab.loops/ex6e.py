items = ("hello", 10, "goodbye", 3, "goodnight", 5)
user_input = input("Enter a value to append: ")

# Unpack the old tuple and add the new value
items = (*items, user_input)

print("Appended tuple with * unpacking:", items)
