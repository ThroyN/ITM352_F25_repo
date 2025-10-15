for num in range(1, 11):
    if num == 5:
        continue   # skip 5
    if num == 8:
        print("Reached 8 — stopping the loop.")
        break      # stop the loop completely
    print(num)
