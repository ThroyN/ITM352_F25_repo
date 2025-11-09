import requests
import pandas as pd

# Query URL
url = "https://data.cityofchicago.org/resource/97wa-y6ff.json?$select=driver_type,count(license)&$group=driver_type"

# Get the data from the API
response = requests.get(url)
data = response.json()  # list of dictionaries

# Convert to DataFrame
df = pd.DataFrame(data)

# Rename the columns to match the requirement
df.columns = ["driver_type", "count"]

# Set index to driver_type
df = df.set_index("driver_type")

# Print the DataFrame
print(df)
