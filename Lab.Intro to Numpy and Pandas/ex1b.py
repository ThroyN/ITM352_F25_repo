import numpy as np

data = [
    (10, 14629),
    (20, 25600),
    (30, 37002),
    (40, 50000),
    (50, 63179),
    (60, 79542),
    (70, 100162),
    (80, 130000),
    (90, 184292)
]

np_array = np.array(data)

print("Percentile Income")
print("---------------------")
for percentile, income in np_array:
    print(f"{percentile:>3}%        ${income:,}")