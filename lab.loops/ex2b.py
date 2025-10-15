evens = [2]   # start with first even number
while evens[-1] < 50:
    evens.append(evens[-1] + 2)

print(evens)
