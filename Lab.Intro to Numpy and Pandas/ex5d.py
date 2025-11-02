import pandas as pd

df = pd.read_csv('/mnt/data/homes_data.csv')

df['units'] = pd.to_numeric(df['units'], errors='coerce')
df['land_sqft'] = pd.to_numeric(df['land_sqft'], errors='coerce')
df['gross_sqft'] = pd.to_numeric(df['gross_sqft'], errors='coerce')
df['year_built'] = pd.to_numeric(df['year_built'], errors='coerce')
df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')

df = df.dropna()
df = df.drop_duplicates()

print(df.head(10))
print(df.shape)
