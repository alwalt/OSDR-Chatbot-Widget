import requests
import json

# Define the study ID
study_id = "488"

# Construct the API endpoint URL
api_url = f"https://osdr.nasa.gov/osdr/data/osd/meta/{study_id}"

# Make the API request and get the response in JSON format
response = requests.get(api_url).json()

# Extract the study information
study_info = response.get("study", {}).get(f"OSD-{study_id}", {}).get("studies", [{}])[0]

# Extracting required information
study_title = study_info.get("title", "Title not found")
study_description = study_info.get("description", "Description not found")

# Extracting factors
factors = study_info.get("factors", [])
factors_info = "\n".join([
    f"{factor.get('factorName', 'Unknown Factor')}: {factor.get('factorType', {}).get('annotationValue', 'No Ontology')}"
    for factor in factors
])

# Extracting organisms (handle if not found)
organisms_info = "No organisms found"
organisms = study_info.get("organisms", {}).get("links", {})
if organisms:
    organisms_info = "\n".join([f"{name}" for name in organisms.keys()])

# Extracting assays from the correct structure
assays_info = "No assays found"
additional_info = study_info.get("additionalInformation", {})
description_content = additional_info.get("description", {})
assays = description_content.get("assays", [])

if assays and isinstance(assays, list):
    assays_info = "\n".join([
        f"{assay.get('Assay Type', 'Unknown Assay Type')} | {assay.get('Device Type', 'Unknown Device Type')} | {assay.get('Device Platform', 'Unknown Device Platform')}"
        for assay in assays
    ])

# Extracting project details from comments
project_info = {}
comments = study_info.get("comments", [])
for comment in comments:
    name = comment.get("name", "Unknown")
    value = comment.get("value", "Not provided")
    project_info[name] = value

# Define the output file path
output_file = f"study_OSD_{study_id}_details.txt"

# Save the extracted information to a file
with open(output_file, 'w') as file:
    file.write(f"Study OSD-{study_id} Title: {study_title}\n\n")
    file.write(f"Study OSD-{study_id} Description: {study_description}\n\n")
    
    file.write("Factors:\n")
    file.write(factors_info + "\n\n")
    
    file.write("Organism(s):\n")
    file.write(organisms_info + "\n\n")
    
    file.write("Assay(s):\n")
    file.write(assays_info + "\n\n")
    
    file.write("Project Information:\n")
    for key, value in project_info.items():
        file.write(f"{key}: {value}\n")

print(f"Study OSD-{study_id} details saved to {output_file}")

