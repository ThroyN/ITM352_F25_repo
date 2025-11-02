import pandas as pd


ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]


df = pd.DataFrame({"Age": ages, "Gender": gender}, index=names)


print("DataFrame:")
print(df)
print("\nSummary Statistics:")
print(df.describe())


avg_age_by_gender = df.groupby("Gender")["Age"].mean()
print("\nAverage Age by Gender:")
print(avg_age_by_gender)
