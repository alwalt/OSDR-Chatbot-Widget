import requests
import json

# Define the study ID
study_id = "488"

# Construct the API endpoint URL
api_url = f"https://osdr.nasa.gov/osdr/data/osd/meta/{study_id}"

# Make the API request and get the response in JSON format
response = requests.get(api_url).json()

# Define the output file path
output_file = f"study_OSD_{study_id}_metadata.json"

# Save the formatted JSON response to a file
with open(output_file, 'w') as file:
    json.dump(response, file, indent=4)

print(f"Study OSD-{study_id} metadata saved to {output_file}")

