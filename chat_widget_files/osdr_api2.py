import requests
import json

# Define the study ID
study_id = "488"

# Construct the API endpoint URL
api_url = f"https://osdr.nasa.gov/osdr/data/osd/meta/{study_id}"

# Make the API request and get the response in JSON format
response = requests.get(api_url).json()

# Extract the study title and description
study_info = response.get("study", {}).get(f"OSD-{study_id}", {}).get("studies", [{}])[0]
study_title = study_info.get("title", "Title not found")
study_description = study_info.get("description", "Description not found")

# Define the output file path
output_file = f"study_OSD_{study_id}_info.txt"

# Save the study title and description to a file
with open(output_file, 'w') as file:
    file.write(f"Study OSD-{study_id} Title: {study_title}\n")
    file.write(f"Study OSD-{study_id} Description: {study_description}\n")

print(f"Study OSD-{study_id} title and description saved to {output_file}")

