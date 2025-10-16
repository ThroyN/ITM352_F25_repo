def get_element(lst, index):
    if index < len(lst):     # check to avoid IndexError
        return lst[index]
    else:
        return "Error: Index out of range"

my_list = [1, 2, 3, 4, 5]
print(get_element(my_list, 2))  # valid index → returns 3
print(get_element(my_list, 5))  # invalid index → returns error message
