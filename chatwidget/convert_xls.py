import pandas as pd

def preprocess_excel_to_csv(excel_file_path, output_csv_path):
    # Load the Excel file
    df = pd.read_excel(excel_file_path)

    # Specify the columns you want to keep
    metadata_columns = [
        'Study', 'Title', 'Organism', 'Project Type', 'Description',
        'Factors', 'Assays', 'Mission', 'Experiment Platform', 'DOI'
    ]

    # Filter the dataframe to only include those columns
    df_filtered = df[metadata_columns]

    # Save the filtered dataframe to a CSV file
    df_filtered.to_csv(output_csv_path, index=False, encoding='utf-8')

    print(f"Processed CSV saved to {output_csv_path}")

if __name__ == "__main__":
    excel_file_path = "osdr_study_metadata.xlsx"  # Path to your original Excel file
    output_csv_path = "osdr_study_metadata.csv"  # Output path for the filtered CSV file
    preprocess_excel_to_csv(excel_file_path, output_csv_path)
    

