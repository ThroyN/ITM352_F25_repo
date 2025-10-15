# Define the tuple
my_tuple = ("hello", 10, "goodbye", 3, "goodnight", 5)

# Initialize a counter
string_count = 0

# Loop through each element in the tuple
for element in my_tuple:
    # Check if the element is a string
    if isinstance(element, str):
        string_count += 1

# Print the result
print("There are", string_count, "strings in the tuple.")

"""
This loop goes through each item in the tuple one at a time and checks if it’s a string.
The isinstance() function is used to test the data type of each element.
If the element is a string, the counter goes up by one.
Once the loop finishes running through all the elements, it prints the total number of strings found.
This setup works because the loop examines every item in the tuple exactly once
and uses a clear condition to identify strings, making the result accurate and easy to understand.
"""
