import pandas as pd
import re
import json
from fuzzywuzzy import process

# Load the dictionary from JSON
def load_mapping_dict(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Function to clean and map values using regular expressions and fuzzy matching
def map_value(value, mapping_dict):
    if pd.isna(value) or value.strip() == "":
        return None

    # Use direct match if exists in the dictionary
    if value.lower() in mapping_dict:
        return process.extractOne(value.lower(), mapping_dict.keys())[0]

    # Apply regex-based corrections for incomplete or improper values
    value = value.lower()
    value = re.sub(r"\s+", "-", value)  # Replace spaces with dashes
    value = re.sub(r"[^a-z0-9-]", "", value)  # Remove special characters

    # Check if corrected value matches
    match = process.extractOne(value, mapping_dict.keys())
    if match and match[1] >= 80:  # Match threshold (80% confidence)
        return match[0]

    # If no match found
    return value  # Return as-is for manual review

# Function to clean the entire DataFrame
def clean_dataframe(input_df, mapping_dict):
    columns_to_map = ["Machine Family", "Series", "Machine Type"]  # Columns to clean and map

    for column in columns_to_map:
        if column in input_df.columns:
            input_df[column] = input_df[column].apply(lambda x: map_value(str(x), mapping_dict))

    return input_df

# Main execution
def main():
    # Input file paths
    input_file = "jane new GcpData- - ComputeEngine (2).csv"
    mapping_file = "index.json"
    output_file = "cleaned_output.csv"

    # Load data
    input_df = pd.read_csv(input_file)
    mapping_dict = load_mapping_dict(mapping_file)

    # Clean the DataFrame
    cleaned_df = clean_dataframe(input_df, mapping_dict)

    # Save the cleaned data
    cleaned_df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")

# Run the script
if __name__ == "__main__":
    main()
