import pandas as pd


data = [
{"company":"Taxi Affiliation Services","payment_type":"Cash","fare":5.65},
{"company":"Choice Taxi Association","payment_type":"Credit Card","fare":8.45},
{"company":"Taxi Affiliation Services","payment_type":"Cash","fare":8.25},
{"company":"Taxi Affiliation Services","payment_type":"Credit Card","fare":11.65},
{"company":"Taxi Affiliation Services","payment_type":"Credit Card","fare":4.45},
{"company":"Dispatch Taxi Affiliation","payment_type":"Credit Card","fare":7.45},
{"company":"Dispatch Taxi Affiliation","payment_type":"Cash","fare":4.25},
{"company":"Dispatch Taxi Affiliation","payment_type":"Cash","fare":5.05},
{"company":"Taxi Affiliation Services","payment_type":"Cash","fare":9.05},
{"company":"Taxi Affiliation Services","payment_type":"Credit Card","fare":11.50},
{"company":"Choice Taxi Association","payment_type":"Cash","fare":6.65},
{"company":"Blue Ribbon Taxi Association Inc.","payment_type":"Cash","fare":8.65},
{"company":"Choice Taxi Association","payment_type":"Cash","fare":6.65},
{"company":"Blue Ribbon Taxi Association Inc.","payment_type":"Cash","fare":5.05},
{"company":"Taxi Affiliation Services","payment_type":"Cash","fare":5.05},
{"company":"Dispatch Taxi Affiliation","payment_type":"Credit Card","fare":5.85}
]


df = pd.DataFrame(data)


print("Taxi Trip Data:")
print(df, "\n")


print("Summary Statistics:")
print(df.describe(), "\n")


median_fare = df["fare"].median()
print("Median Fare:", median_fare)
