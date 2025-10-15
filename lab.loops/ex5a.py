celebrities_tuple = ("Taylor Swift", "Lionel Messi", "Max Verstappen", "Keanu Reeves", "Angelina Jolie")
ages_tuple = (35, 37, 27, 60, 49)

celebrities_list = []
ages_list = []

for celeb in celebrities_tuple:
    celebrities_list.append(celeb)

for age in ages_tuple:
    ages_list.append(age)

celeb_dict = {
    "celebrities": celebrities_list,
    "ages": ages_list
}

print(celeb_dict)
