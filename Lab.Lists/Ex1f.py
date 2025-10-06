first_name = input("Enter first name: ")
middle_name = input("Enter middle name: ")
last_name = input("Enter last name: ")





name_parts = [first_name, middle_name, last_name]
full_name = "{} {} {}".format(*name_parts)
print(full_name)
