from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="./osdr_study_metadata.csv")

#data = loader.load()

import pandas as pd

df = pd.read_csv("osdr_study_metadata.csv")
import pandas as pd

print([repr(col) for col in df.columns])  # Display all column names with their exact representations
print(df.columns) 
#print(df.columns)  # Print out all column names to verify
#print(df['Study'].isnull().sum())  # Count the number of null values in the 'Study' column
#print(df['Study'].apply(lambda x: x.strip() == '').sum())  # Count empty (but non-null) strings
#print(df['Study'].duplicated().sum())  # Count duplicate values in the 'Study' column

#print(df['Study'].head(10))  # Print the first 10 values in the 'Study' column

#print(data)
