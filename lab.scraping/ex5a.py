import requests

# Query URL (returns driver_type and count of licenses)
url = "https://data.cityofchicago.org/resource/97wa-y6ff.json?$select=driver_type,count(license)&$group=driver_type"

# Make GET request
response = requests.get(url)

# Convert response to JSON (Python list of dictionaries)
data = response.json()

# Print the response
print(data)
