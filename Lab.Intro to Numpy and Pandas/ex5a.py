import pandas as pd


df = pd.read_csv('/mnt/data/homes_data.csv')


print("Dimensions of DataFrame:", df.shape)


print(df.head(10))
