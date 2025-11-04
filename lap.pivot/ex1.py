import pandas as pd

url = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"
df = pd.read_csv(url)


print(df.head())

# Show the data types of each column
print("\nColumn Data Types:")
print(df.dtypes)
