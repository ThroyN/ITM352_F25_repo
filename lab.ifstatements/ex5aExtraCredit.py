def movie_price(age, weekday, matinee):
    price = 14  
    if age >= 65:
        price = min(price, 8)

    if weekday == "Tuesday":
        price = min(price, 10)
    if matinee:
        if age >= 65:
            price = min(price, 5)   # senior matinee
        else:
            price = min(price, 8)   # regular matinee
    return price
age = 70
weekday = "Tuesday"
matinee = True
print(f"Age: {age}")
print(f"Weekday: {weekday}")
print(f"Matinee: {matinee}")
print(f"Ticket Price: ${movie_price(age, weekday, matinee)}")
