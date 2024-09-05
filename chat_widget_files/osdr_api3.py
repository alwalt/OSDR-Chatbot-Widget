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
factors_info = "\n".join([f"{factor.get('factor', 'Unknown Factor')}: {factor.get('ontology_concept', 'No Ontology')}" for factor in factors])

# Extracting organisms
organisms = study_info.get("organisms", {}).get("links", {})
organisms_info = "\n".join([f"{name}" for name in organisms.keys()])

# Extracting assays (adjusted to handle a list)
assays = study_info.get("assays", [])
assays_info = "\n".join([
    f"{assay.get('measurement', 'Unknown Measurement')} | {assay.get('technology', 'Unknown Technology')} | {assay.get('device_platform', 'Unknown Device Platform')}"
    for assay in assays
])

# Extracting project details
project_info = {
    "Payload Identifier": study_info.get("payload_identifier", "Payload Identifier not found"),
    "Project Title": study_info.get("project_title", "Project Title not found"),
    "Project Type": study_info.get("project_type", "Project Type not found"),
    "Flight Program": study_info.get("flight_program", "Flight Program not found"),
    "Experiment Platform": study_info.get("experiment_platform", "Experiment Platform not found"),
    "Sponsoring Agency": study_info.get("sponsoring_agency", "Sponsoring Agency not found"),
    "NASA Center": study_info.get("nasa_center", "NASA Center not found"),
    "Funding Source": study_info.get("funding_source", "Funding Source not found"),
}

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

