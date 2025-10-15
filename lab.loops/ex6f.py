items = ("hello", 10, "goodbye", 3, "goodnight", 5)
user_input = input("Enter a value to append: ")

# Convert to list to allow append
items_list = list(items)
items_list.append(user_input)

# Convert back to tuple
items = tuple(items_list)

print("Appended tuple via list conversion:", items)

