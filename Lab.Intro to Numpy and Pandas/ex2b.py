import pandas as pd

# Data lists
ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

# Create DataFrame with names as index
df = pd.DataFrame({"Age": ages, "Gender": gender}, index=names)

# Print DataFrame and summary
print(df)
print(df.describe())
