def multiply(x, y):
    product = 0
    for _ in range(y):     # loop y times
        product += x       # add x repeatedly
    return product

first = int(input("Enter the first number: "))
second = int(input("Enter the second number: "))

prod = multiply(first, second)
print(f"The product of {first} and {second} is {prod}")
