import pandas as pd


df = pd.read_csv('/mnt/data/homes_data.csv')


df["units"] = pd.to_numeric(df["units"], errors="coerce")


df_filtered = df[df["units"] >= 500]


cols_to_drop = ["id", "block", "lot", "easement", "land_sqft", "gross_sqft"]
df_filtered = df_filtered.drop(columns=cols_to_drop, errors="ignore")


print(df_filtered.head(10))
